from final_pdf_processing import EnemPDFextractor


extrac1 = EnemPDFextractor("pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf","pdfs_enem/2022/2022_GB_impresso_D1_CD1.pdf","output", "txt")

extrac1.extract_one_pdf()