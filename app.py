import os
import nltk
import urllib
import json
#import webbrowser
import collections
import sys
import argparse
from itertools import chain, combinations
from nltk.corpus import stopwords
import re

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from jinja2 import evalcontextfilter, Markup, escape

# Initialize the Flask application
app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = 'uploads/'

app.config['ALLOWED_EXTENSIONS'] = set(['txt'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
              
        return render_template('index.html')

@app.route('/process',methods=['POST'])
def process():
    #initialize global array
    found_headers = []
    row_values=[]
    final=[]
    """
    def generate_table(filename, headers, values_list,counter):
        '''
        @param filename: name of the file to write the table to
        @param headers: a list of coloumn headers
        @param values_list: a list of rows to be written to the table
        '''
        header_line = ",".join(headers)
        with open(filename, "a+") as f:
            print 'counter is %d' %counter
            if counter == 0 :
                f.write("%s\n" % header_line)
            else:
                print 'skipping'
            #print 'headers ', headers
            for values in values_list: #values is a list of tokens
                row_items = []
                #print 'values ', values
                for coloumn_name in headers:
                    #print 'column ', coloumn_name,
                    if coloumn_name in values:
                        row_items.append('1')
                        #print '1'
                    else:
                        row_items.append('0')
                        #print '0'
                row_line = ",".join(row_items)
                f.write("%s\n" % row_line)
                """
    file_diseases = open('uploads/medical_dic.txt', 'r')
    DISEASES = set([d.lower() for d in file_diseases.read().split()])

    #finding common headers from all files
    def find_headers():
        j=1
        while(os.path.exists("uploads/transcription%d.txt" %j)):
            file_transcription = open('uploads/transcription%d.txt'%j, 'r')
            transcription_tokens = [t.lower() for t in file_transcription.read().split()]

            #stop word removal
            looper = 0
            stops = set(stopwords.words('english'))
            for line in transcription_tokens:
                for w in line.split():
                    if w not in stops:
                        transcription_tokens[looper] = w
                        looper += 1

            #Stemming
            looper = 0
            for token in transcription_tokens:
                transcription_tokens[looper] = re.sub('ing', '', transcription_tokens[looper])
                looper += 1

           
            #Lemmatization
            lmtzr = nltk.stem.wordnet.WordNetLemmatizer()
            looper = 0
            for token in transcription_tokens:
                transcription_tokens[looper] = lmtzr.lemmatize(token)
                looper += 1
            for found in list((set(transcription_tokens).intersection(DISEASES))):
                found_headers.append(found)
            j=j+1
        return j

    #insert the headers into the csv
    def insert_headers():
        header_line = ",".join(found_headers)
        filename='1.csv'
        with open(filename, "a+") as f:
            f.write("%s\n" % header_line)


    def do_rest():
        for index,i in enumerate(found_headers):
            j=1
            temp=[]
            while(os.path.exists("uploads/transcription%d.txt" %j)):
                found = 0
                with open('uploads/transcription%d.txt'%j, 'r') as fileinput:
                    for line in fileinput:
                        line = line.lower()
                        if i in line:
                        
                            found = 1
                           
                            continue
                    if found == 1:
                        temp.append('TRUE')
                        """
                        if i in open("uploads/medicine_dic.txt").read().lower():
                            temp.append("(med)" + i)
                        elif i in open("uploads/disease_dic.txt").read().lower():
                            temp.append("(dis)" + i)
                        else:
                            temp.append(i)
                            """
                    else:
                        temp.append('')
                j=j+1
            row_values.append(temp)

        #taking transpose to get the final array
        final= map(list,map(None,*row_values))
        print final
        return final

    def insert_rest():
        for i in range(len(final)):
            row_line = ",".join(final[i])
            filename='1.csv'
            with open(filename, "a+") as f:
                f.write("%s\n" % row_line)

    cnt=find_headers()
    #sorted = sort list, list(set(x)) = convert to set and then back to list to remove duplicates
    found_headers=sorted(list(set(found_headers)))
   # print found_headers
    insert_headers()
    final=do_rest()
    insert_rest()
    return render_template('index.html')



@app.route('/apriori', methods=['POST'])
def apriori():
    os.system("python apriori.py")

    fr = open("output.txt","r")
    r = fr.read()
    r = r.replace('\n','<br/>')
    

    return render_template("home.html",x = r)   
     
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == '__main__':
    app.run(debug=True)
