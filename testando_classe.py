from Enem_pdf_parser_class import EnemPDFextractor


#extrac_day2 = EnemPDFextractor("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output2", "txt")
#extract_day1 = EnemPDFextractor("txt")

#extract_day1.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf","pdfs_enem/2022/2022_GB_impresso_D1_CD1.pdf","output")
#extract_day1.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output2",)


json_day_one = EnemPDFextractor("json")

json_day_one.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf","pdfs_enem/2022/2022_GB_impresso_D1_CD1.pdf","output_json")