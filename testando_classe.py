from Enem_PDF_extractor import EnemPDFextractor


#extrac_day2 = EnemPDFextractor("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output2", "txt")
extract_txt = EnemPDFextractor("JSON", process_questions_with_images=False)
extract_txt2 = EnemPDFextractor("txt")


#extract_txt2.extract_pdf("pdfs_enem/2023/2023_PV_impresso_D2_CD7.pdf","pdfs_enem/2023/2023_GB_impresso_D2_CD7.pdf","output_nimages_23_2")

extract_txt.extract_pdf("pdfs_enem/2020/2020_PV_impresso_D1_CD1.pdf","pdfs_enem/2020/2020_GB_impresso_D1_CD1.pdf","outputs_dirs/output_20_1_no_images")
# "pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf","pdfs_enem/2022/2022_GB_impresso_D1_CD1.pdf","output_22_1"

#json = EnemPDFextractor("json")

#json.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output_json2")
#json.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf","pdfs_enem/2022/2022_GB_impresso_D1_CD1.pdf","output_json2")


#image_extractor = EnemPDFextractor(ignore_questions_with_images=False,output_type="json")

#image_extractor.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output_fitz2")