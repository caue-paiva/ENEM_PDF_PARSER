from Enem_pdf_parser_class import EnemPDFextractor


#extrac_day2 = EnemPDFextractor("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output2", "txt")
extract_txt = EnemPDFextractor("txt")

extract_txt.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output_fitz_no_images2")
#extract_txt.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output2",)


#json = EnemPDFextractor("json")

#json.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output_json2")
#json.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf","pdfs_enem/2022/2022_GB_impresso_D1_CD1.pdf","output_json2")


#image_extractor = EnemPDFextractor(ignore_questions_with_images=False,output_type="json")

#image_extractor.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output_fitz2")