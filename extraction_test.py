from Enem_PDF_extractor import EnemPDFextractor
import time
image_extract =  [True,False]
day_color_identifier = [(1,1), (2,7)] #tupla para acessar as provas e gabaritos do primeiro e segundo dia (caderno azul)
years = [23,22,21,20]
output_file = ["txt", "json"]
pdf_folder_path = "pdfs_enem"

no_images_timer: float = 0.0
images_timer: float = 0.0
execution_counter:int = 0 


for image in image_extract:
    for output in output_file:
        text_extractor = EnemPDFextractor(output_type=output, process_questions_with_images=image)
        image_identifier = "img" if image else "" 
        for i, j in day_color_identifier:
            for year in years: 
                time_before:float = time.time()
                text_extractor.extract_pdf(
                    test_pdf_path=f"pdfs_enem/20{year}/20{year}_PV_impresso_D{i}_CD{j}.pdf",
                    answers_pdf_path=f"pdfs_enem/20{year}/20{year}_GB_impresso_D{i}_CD{j}.pdf", 
                    extracted_data_path=f"test_output/20{year}_D{i}_{image_identifier}"
                    )
                time_passed = time.time() - time_before
                execution_counter += 1
                if image:
                    images_timer +=  time_passed
                else:
                    no_images_timer += time_passed

execution_counter /= 2  #metades das execuções são extraindo imagens, metade não

print(f"tempo médio extrair PDFs sem imagens {no_images_timer/execution_counter},  tempo médio para extrair os pdfs com as images {images_timer/execution_counter}")

           


            



#extrac_day2 = EnemPDFextractor("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output2", "txt")
#extract_txt = EnemPDFextractor("JSON", process_questions_with_images=False)
#extract_txt2 = EnemPDFextractor("txt")


#extract_txt2.extract_pdf("pdfs_enem/2023/2023_PV_impresso_D2_CD7.pdf","pdfs_enem/2023/2023_GB_impresso_D2_CD7.pdf","output_nimages_23_2")

#extract_txt.extract_pdf("pdfs_enem/2020/2020_PV_impresso_D1_CD1.pdf","pdfs_enem/2020/2020_GB_impresso_D1_CD1.pdf","outputs_dirs/output_20_1_no_images")
# "pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf","pdfs_enem/2022/2022_GB_impresso_D1_CD1.pdf","output_22_1"

#json = EnemPDFextractor("json")

#json.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output_json2")
#json.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D1_CD1.pdf","pdfs_enem/2022/2022_GB_impresso_D1_CD1.pdf","output_json2")


#image_extractor = EnemPDFextractor(ignore_questions_with_images=False,output_type="json")

#image_extractor.extract_pdf("pdfs_enem/2022/2022_PV_impresso_D2_CD7.pdf","pdfs_enem/2022/2022_GB_impresso_D2_CD7.pdf","output_fitz2")