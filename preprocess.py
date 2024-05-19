import keras_ocr, os, subprocess
import pandas as pd
from tqdm import tqdm

pipeline = keras_ocr.pipeline.Pipeline()
DIR = "dr_prescriptions"

def set_custom_words():
    """
    Creates custom dictionary for cspell spell checking. 
    NOTE: Make sure to add the dictionary to cspell.json file
    """
    # Read .xlsx file
    df = pd.read_excel('500 PRS + Slip Image & Data/Physician Database 500 PRS.xlsx')
    dr_names = df["PHY_NM"].apply(lambda x: x.lower().split(" ")).tolist()

    dr_name_set = set()
    for dr_name in dr_names:
        dr_name_set.update(dr_name)

    # Write dr. names to a file for cspell spell checking
    with open("custom-words.txt", "w") as f:
        for dr_name in dr_name_set:
            f.write(dr_name + "\n")

def get_predictions_list(image_paths: list[str]) -> None:
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    for img_path in tqdm(image_paths):
        image = [keras_ocr.tools.read(img_path)]
        prediction_groups = pipeline.recognize(image)
        text = " ".join([word for word, box in prediction_groups[0]])
        filename = os.path.join(DIR, f"{os.path.splitext(os.path.basename(img_path))[0]}.txt")
        with open(filename, "w") as f:
            f.write(text)


def make_corrections(text_path):
    result = subprocess.run(["./cspell_script.sh", text_path], capture_output=True)
    words_to_corrections = {}
    errors = result.stdout.splitlines()
    for error in errors:
        error = error.decode("utf-8")
        mistake = error.split(" ")[4][1:-1]
        corrections = error.split("Suggestions: ")[-1]
        best_correction = corrections.split(", ")[0][1:]
        words_to_corrections[mistake] = best_correction

    with open(text_path, "r") as f:
        text = f.read()
    
    for mistake, correction in words_to_corrections.items():
        text = text.replace(mistake, correction)

    with open(text_path, "w") as f:
        f.write(text)


if __name__ == "__main__":
    # Get OCR Output in directory called "dr_prescriptions"
    file_count = 50  # Number of files to process (MAX: 300)
    dir_path = "500 PRS + Slip Image & Data/Dr. PRS (300)"
    get_predictions_list([os.path.join(dir_path, img) for img in os.listdir(dir_path)[:file_count]])

    # Make corrections to the text files in "dr_prescriptions" directory
    # NOTE: REMEMBER TO START DOCKER FOR CSPELL, else cspell_script.sh will not work
    dir_path = "dr_prescriptions"
    for text_file in os.listdir(dir_path):
        make_corrections(os.path.join(dir_path, text_file))