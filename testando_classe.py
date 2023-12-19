from final_pdf_processing import EnemPDFextractor


extrac1 = EnemPDFextractor("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output2", "txt")

extrac1.extract_one_pdf()