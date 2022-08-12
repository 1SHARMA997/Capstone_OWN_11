# Necessary modules to import
import shutil
import streamlit as st
import difflib

from matplotlib import pyplot as plt

from markUp import markUpDifferences
from diffReport import diffReport, html_output

from pdfParser import pdfparser
import fuzzyCompare
import pandas as pd
import os
import matplotlib.pyplot as plth
import smtplib
# For mail automation

#email ID configured to recieve status reports
sender = "hphulara996@gmail.com>"
receiver = "hphulara211@gmail.com>"

# Email Body
message = f"""\
Subject: PDF Comparison ran successfully.
To: {receiver}
From: {sender}

Hi User, 
PDF Comparison ran successfully. Please download the detailed HTML report with ratios.

Thanks"""

#Establishing the folder structure within working directory
shutil.rmtree('tempDir')
os.mkdir("tempDir")
os.mkdir("tempDir/input1")
os.mkdir("tempDir/input2")

#Setting streamlit page configurations
st.set_page_config(page_title='PDF Compare', page_icon='📄', initial_sidebar_state='collapsed', layout="wide")

#Function to upload files to a given folder path with iterative file names
def save_uploadedfile(uploadedfile, filenum, path):
    try:
        with open(os.path.join("tempDir", path, "file" + str(filenum) + ".pdf"), "wb") as f:
            f.write(uploadedfile.getbuffer())
            f.close()
    except Exception as er:
        st.error("Error while uploading the files {} ".format(er))


def main():
    st.markdown("<h2 style='text-align: center; color: grey;'>PDF Comparision</h2>", unsafe_allow_html=True)

    try:
        # Creating file upload widget to upload PDF Files for comparison
        input1 = st.file_uploader('Please upload 1st file or multiple files', type=['pdf'], accept_multiple_files=True)
        i = 1
        for input_file in input1:
            if input_file is not None:
                save_uploadedfile(input_file, i, "input1")
                i += 1
        input2 = st.file_uploader('Please upload your 2nd file or multiple files', type=['pdf'],
                                  accept_multiple_files=True)
        i = 1
        for input_file in input2:
            if input_file is not None:
                save_uploadedfile(input_file, i, "input2")
                i += 1
    except Exception as er:
        st.error("Error while uploading the files {} ".format(er))
    else:
        try:
            # Provide radio button input options for the various partial ratios made available in DiffReport
            select_ratio = ['Partial Ratio', 'qRatio', 'wRatio', "tokenSortRatio", 'partialRatio', 'tokenSetRatio',
                            'partialTokenSortRatio']
            choice = st.radio('Please select the Partial Ratio', select_ratio)
            st.write('Select options to exclude from analytics:')

            ncol = st.sidebar.number_input('Number of characters/ Substring to exclude', 0, 20, 1)
            cols = st.columns(ncol)

            #Creating 3 columns in streamlit to stack input fields adjacent to each other
            col1, col2, col3 = st.columns(3)
            st.write("List of characters/ Substring to exclude")
            with col1:
                text_1 = st.text_input('Option 1', key='1')
            with col2:
                text_2 = st.text_input('Option 2', key='2')
            with col3:
                text_3 = st.text_input('Option 3', key='3')
            st.write(
                "For more characters or substrings to exclude from analytics, please provide them in the below text box seperated by a comma , Eg: 'text1,text2' ")

            #Splitting the comma seperated text into a list of strings to remove from comparison
            comma_sep_input = st.text_input('Comma seperated characters to exclude')
            list_to_exclude = comma_sep_input.split(',')
            list_to_exclude += [text_1, text_2, text_3]

            #Validating the number files provided for comparison are matching
            files_in_input1 = len(
                [name for name in os.listdir('tempDir/input1') if os.path.isfile(os.path.join('tempDir/input1', name))])
            files_in_input2 = len(
                [name for name in os.listdir('tempDir/input2') if os.path.isfile(os.path.join('tempDir/input2', name))])
        except Exception as er:
            st.error("Error  {} ".format(er))
        else:
            try:
                results = {}
                n_pass = 0
                n_fail = 0
                f = ""
                if st.button("Get the analysis"):
                    if (files_in_input1 != files_in_input2):
                        st.write(
                            "Number of files in input 1 does not match with number of files in input 2, Please provide the same number of files for one to one comparison")
                    else:
                        for i in range(1, files_in_input1 + 1):
                            #Passing all provided inputs to the DiffReport package for processing the PDFs
                            df, cmp_file = diffReport("tempDir/input1/file" + str(i) + ".pdf",
                                                      "tempDir/input2/file" + str(i) + ".pdf", html_return=False,
                                                      partial_ratio=choice, exlude_analytics=list_to_exclude,
                                                      path_file_output="tempDir/output" + str(i) + "/")
                            file_output = "Output/"
                            html_file = html_output(df, file_output, cmp_file)
                            # st.markdown(html_file, unsafe_allow_html=True)
                            f = "file" + str(i)
                            if len(df.index) != 0:
                                results[f] = "Fail"
                                n_fail += 1
                            else:
                                results[f] = "Pass"
                                n_pass += 1

                        #Display results from DiffReport to the user
                        st.write(results)
                        st.write(n_pass)
                        st.write(n_fail)
                        res = [n_pass, n_fail]
                        show_res = 0
            except Exception as er:
                st.error("Error while calling the diff report {} ".format(er))
            else:
                try:
                    #Visualizing the results of the run in Streamlit using matplotlib charts
                    plt.pie(res, colors=['#9BBF85', '#D091BB'], labels=["Pass", "Fail"],
                            autopct='%2.3f%%', pctdistance=0.85)

                    #Creating a donut chart from the visualization
                    centre_circle = plt.Circle((0, 0), 0.60, fc='white')
                    fig = plt.gcf()
                    fig.gca().add_artist(centre_circle)
                    # Adding Title of chart
                    plt.title('Results')
                    st.write(pd.DataFrame(results.items(), columns=["File", "Result"]))
                    coll1, coll2, coll3 = st.columns(3)
                    #st.write("List of characters/ Substring to exclude")
                    with coll1:
                        st.pyplot(fig=fig)
                    with coll2:
                        pass
                        #st.pyplot(fig=fig)
                    with coll3:
                        pass
                        #st.pyplot(fig=fig)
                    #Sending results to SMTP server for email reports on the comparison
                    with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
                        server.login("c4212998cf94d0", "840460b339dac3")
                        server.sendmail(sender, receiver, message)
                except:
                    st.write("")


if __name__ == '__main__':
    main()