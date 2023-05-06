from django.http import FileResponse
from django.shortcuts import render
from textsummarization.forms import DocumentForm
from textsummarization.models import DocumentModel
# Create your views here.
from textsummarization.summarize import sum_it_up
import re

import cv2
import os, argparse
import pytesseract
from PIL import Image
# importing required modules
import PyPDF2

def readimage(image):
    # We then read the image with text
    images = cv2.imread(image)

    # convert to grayscale image
    gray = cv2.cvtColor(images, cv2.COLOR_BGR2GRAY)

    cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # memory usage with image i.e. adding image to memory
    filename = "{}.jpg".format(os.getpid())
    cv2.imwrite(filename, gray)
    text = pytesseract.image_to_string(Image.open(filename))
    os.remove(filename)

    return text

def readPdf(file):

    # creating a pdf file object
    pdfFileObj = open(file, 'rb')

    # creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    # printing number of pages in pdf file
    print(pdfReader.numPages)

    # creating a page object
    pageObj = pdfReader.getPage(0)

    # extracting text from page
    data=pageObj.extractText()

    # closing the pdf file object
    pdfFileObj.close()

    return data

def getDocuments():

    documents = []

    for documentModel in DocumentModel.objects.all():
        documentModel.document = str(documentModel.document).split("/")[1]
        print("Document Path:", documentModel.document)
        documents.append(documentModel)

    return documents

def uploaddocument(request):

    documentForm = DocumentForm(request.POST, request.FILES)

    if documentForm.is_valid():
        documentModel = DocumentModel()
        documentModel.document = documentForm.cleaned_data["document"]
        documentModel.save()
        return render(request, 'index.html', {"message": "Document Uploaded Successfully"})

    return render(request, 'index.html', {"message": "Invalid Request"})

def viewdocuments(request):
    return render(request, "documents.html", {"documents": getDocuments()})

def deletedocument(request):

    id= request.GET['id']

    DocumentModel.objects.filter(id=id).delete()

    return render(request, "documents.html", {"documents": getDocuments()})

def downloaddocument(request):
    id = request.GET['id']

    documentModel=DocumentModel.objects.filter(id=int(id)).first()
    print(str(documentModel.document))
    response = FileResponse(open(str(documentModel.document), 'rb'))
    return response

def getsummary(request):

    content=""

    for documentModel in DocumentModel.objects.all():

        file=str(documentModel.document)

        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            data=str(readimage(file))
            content = content +data
            print("IMAGE:",data,"--------------------\n")
        elif file.lower().endswith('.pdf'):
            data=str(readPdf(file))
            content = content + data
            print("PDF:", data, "--------------------\n")
        else:
            f=(open(str(documentModel.document), 'r'))
            data=""
            for line in f.readlines():
                data=data+line
            content = content + data
            print("Text:", data, "--------------------\n")

    result=sum_it_up(content)
    print("Result:", result, "--------------------\n")
    final_content=""
    for res in result:
        txt=res.replace("\n", " ")
        final_content=final_content+str(txt);
    return render(request, 'result.html', {"message":final_content})

