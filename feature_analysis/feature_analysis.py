
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../feature_extraction"))
from feature_extraction_func import NGramFeatureExtractor, LDAFeatureExtractor, EmpathFeatureExtractor

output_folder = "data/feature_analysis_output"
os.makedirs(output_folder, exist_ok=True)

# N-Gram Analysis
ngram_extractor = NGramFeatureExtractor()
ngram_extractor.extract_features()
ngram_extractor.save_wordclouds(output_folder)

# Empath Analysis
empath_extractor = EmpathFeatureExtractor()
empath_extractor.extract_empath_features()
empath_extractor.analyze_correlation()
empath_extractor.save_correlation_table(output_folder)

# LDA Analysis
lda_extractor = LDAFeatureExtractor(num_topics=20)
lda_extractor.run_analysis_pipeline()
lda_extractor.save_tsne_visualization(output_folder)