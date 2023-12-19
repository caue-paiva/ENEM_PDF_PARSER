from final_pdf_processing import EnemPDFextractor


#extrac_day2 = EnemPDFextractor("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output2", "txt")
extract_day1 = EnemPDFextractor("pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf","pdfs_enem/2022/2022_GB_impresso_D1_CD1.pdf","output", "txt")

extract_day1.extract_one_pdf()