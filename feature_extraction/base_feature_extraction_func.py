###############################################################################
#  IMPORTS
###############################################################################
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import matplotlib.pyplot as plt
import pandas as pd

###############################################################################
#  CONFIGURATION CONSTANTS
###############################################################################

# Default folders and labels for preprocessed posts
DEFAULT_FOLDERS = {
    "depression": {"path": os.path.join("data", "preprocessed_posts", "depression"), "label": 1},
    "standard": {"path": os.path.join("data", "preprocessed_posts", "standard"), "label": 0},
    "breastcancer": {"path": os.path.join("data", "preprocessed_posts", "breastcancer"), "label": 2},
}

# Default output folder for feature extraction data
DEFAULT_OUTPUT_FOLDER = os.path.join("data", "feature_extracted_data")

# File extension to consider for input files
TXT_FILE_EXTENSION = ".txt"

# Configuration for summary table plotting
FIGSIZE_SUMMARY = (8, 4)
SUMMARY_TITLE = "Summary of Feature Extraction Methods"
SUMMARY_TITLE_FONT_SIZE = 16
SUMMARY_TITLE_FONT_WEIGHT = "bold"
SUMMARY_TITLE_PAD = 20
SUMMARY_TABLE_COLUMN_INDICES = [0, 1, 2]
TABLE_FONT_SIZE = 10
TABLE_HEADER_FONT_SIZE = 12
TABLE_SCALE_FACTOR = (1.2, 1.2)
TABLE_DPI = 300

# Configuration for Empath table plotting
FIGSIZE_EMPATH = (12, 6)
EMP_TABLE_HEADER_FONT_SIZE = 14

###############################################################################
#  BASE CLASS
###############################################################################
class FeatureExtractor:
    def __init__(self, *, folders=None, output_folder=DEFAULT_OUTPUT_FOLDER):
        self.folders = folders if folders else DEFAULT_FOLDERS
        self.documents, self.labels = self.load_documents_and_labels()
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

    def load_documents_and_labels(self):
        documents, labels = [], []
        total_loaded = 0

        for category, data in self.folders.items():
            folder_path = data["path"]
            if not os.path.exists(folder_path):
                print(f"Warning: Folder '{folder_path}' does not exist.")
                continue

            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if not file_path.lower().endswith(TXT_FILE_EXTENSION):
                    continue  # Skip non-text files

                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        lines = file.readlines()
                        content_start = next(
                            (i + 1 for i, line in enumerate(lines) if not line.strip()), 0
                        )
                        post_content = ' '.join(lines[content_start:]).strip()

                        if post_content:
                            documents.append(post_content)
                            labels.append(data["label"])
                            total_loaded += 1
                except FileNotFoundError:
                    print(f"Error: File '{file_path}' not found.")
                except PermissionError:
                    print(f"Error: Permission denied for file '{file_path}'.")
                except Exception as e:
                    print(f"Unexpected error reading file '{file_path}': {e}")

        print(f"Loaded {total_loaded} documents (only the post content).")
        return documents, labels

    def preprocess_text(self, text):
        """
        Tokenize, lowercase, remove stopwords, and stem.
        """
        stop_words = set(stopwords.words('english'))
        stemmer = PorterStemmer()
        tokens = word_tokenize(text.lower())
        return [stemmer.stem(word) for word in tokens if word.isalpha() and word not in stop_words]

    def save_to_csv(self, data, filename):
        """
        Save data to a CSV file.
        """
        # Construct the full file path
        if not filename.startswith(self.output_folder):
            file_path = os.path.join(self.output_folder, filename)
        else:
            file_path = filename

        # Debug: Print the path being used
        print(f"Saving file to: {file_path}")

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save the file if it doesn't already exist
        if not os.path.exists(file_path):
            data.to_csv(file_path, index=False)
            print(f"Saved to {file_path}.")
        else:
            print(f"File already exists at {file_path}.")


###############################################################################
#  SUMMARY / TABLE GENERATION FUNCTIONS
###############################################################################

def generate_summary_table(ngram_extractor, empath_extractor, lda_extractor, output_file=None):
    """
    Create and save a summary table comparing feature extraction methods.
    """
    # Extract the number of features from each extractor
    unigram_count = len(ngram_extractor.unigram_feature_names)
    bigram_count = len(ngram_extractor.bigram_feature_names)
    empath_feature_count = empath_extractor.features.shape[1] - 1  # Exclude label column
    lda_feature_count = lda_extractor.num_topics  # Number of topics in LDA

    # Build the summary data
    summary_data = [
        ["N-grams", "Unigram", unigram_count],
        ["N-grams", "Bigram", bigram_count],
        ["Linguistic Dimensions", "Empath", empath_feature_count],
        ["Topic Modeling", "LDA", lda_feature_count]
    ]

    # Convert to a DataFrame
    summary_table = pd.DataFrame(summary_data, columns=["Feature Type", "Methods", "Number of Selected Features"])

    # Plot the table
    fig, ax = plt.subplots(figsize=FIGSIZE_SUMMARY)
    ax.axis('tight')
    ax.axis('off')
    plt.title(SUMMARY_TITLE, fontsize=SUMMARY_TITLE_FONT_SIZE, fontweight=SUMMARY_TITLE_FONT_WEIGHT, pad=SUMMARY_TITLE_PAD)

    # Create the table 
    table = ax.table(
        cellText=summary_table.values, 
        colLabels=summary_table.columns, 
        cellLoc='center', 
        loc='center'
    )

    # Style adjustments
    table.auto_set_font_size(False)
    table.set_fontsize(TABLE_FONT_SIZE)
    table.auto_set_column_width(SUMMARY_TABLE_COLUMN_INDICES)
    table.scale(*TABLE_SCALE_FACTOR)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_fontsize(TABLE_HEADER_FONT_SIZE)
            cell.set_text_props(weight="bold")
            cell.set_linewidth(1.5)
        if col == 0:
            cell.set_text_props(weight="bold")
        if row > 0 and (row % 2 == 0):
            cell.set_facecolor("#f0f0f0")

    plt.savefig(output_file, bbox_inches="tight", dpi=TABLE_DPI)
    print(f"Table saved to {output_file}")
    plt.show()

    return summary_table


def generate_empath_table(input_csv, output_file=None):
    """
    Create and save a correlation table for EMPATH features.
    """
    empath_df = pd.read_csv(input_csv)
    empath_df["Empath Category"] = empath_df["Empath Category"].str.capitalize()
    empath_df = empath_df.sort_values(by="P-Value").head(10).sort_values(by="Empath Category")
    empath_df["P-Value"] = empath_df["P-Value"].apply(lambda x: f"{x:.3e}" if x < 0.001 else round(x, 3))
    empath_df["Correlation"] = empath_df["Correlation"].round(3)
    empath_df.rename(
        columns={
            "Empath Category": "Category",
            "Example Word": "Example Word",
        },
        inplace=True,
    )

    fig, ax = plt.subplots(figsize=FIGSIZE_EMPATH)
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(
        cellText=empath_df.values,
        colLabels=empath_df.columns,
        cellLoc="center",
        loc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(TABLE_FONT_SIZE)
    table.auto_set_column_width(col=list(range(len(empath_df.columns))))
    for key, cell in table.get_celld().items():
        row, col = key
        if row == 0:  # Header row
            cell.set_text_props(weight="bold")
            cell.set_fontsize(EMP_TABLE_HEADER_FONT_SIZE)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file, bbox_inches="tight", dpi=TABLE_DPI)
    print(f"Table saved to {output_file}")
    plt.show()
