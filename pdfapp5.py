## generate the descrition from the previous transactions using sqldb agent in langchain

import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts.few_shot import FewShotPromptTemplate
import pandas as pd
import pdfrw
from pdfrw import PdfReader, PdfWriter
import matplotlib.pyplot as plt
import re
import random

#mykey = "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"

#from langchain.llms import AzureOpenAI
#import openai
#import os
 
#os.environ["OPENAI_API_TYPE"] = "azure"
#os.environ["OPENAI_API_KEY"] = "ffdeca15444e422ba37b2dba6f77552f"
#os.environ["OPENAI_API_BASE"] = "https://dfpgptinstance.openai.azure.com/"
#os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"
 
#llm = AzureOpenAI(deployment_name="dfp",model_name="gpt-35-turbo")
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage
import openai
import os

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_KEY"] = "dc1053592cd447a4b1122dd8ce2e696e"
os.environ["OPENAI_API_BASE"] = "https://dfpgptinstance.openai.azure.com/"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"

llm = AzureChatOpenAI(deployment_name="dfp16k",model_name="gpt-35-turbo-16k")

def query_llm_response(data):
    prompt = PromptTemplate(
        input_variables=["data"],
        template=""" Given the list of financial transactions provided in the {data}, identify potential instances of money laundering based solely on this dataset. If the dataset contains transactions from single sender to multiple receiver accounts, multiple senders to single receiver account. similarly for different currencies, then display money laundering transactions with detailed explanation. For example 
Example: 1

If the transactions are happening in the following pattern
Now let's break down the individual transactions:
* 		2022/09/01 02:38, 001812, 80279F810, 0110, 8000A94C0, 10154.74, Australian Dollar, 10154.74, Australian Dollar, ACH, 1: This line represents a transaction that occurred on September 1, 2022. It involves a certain amount (10154.74 Australian Dollars) transferred via an ACH (Automated Clearing House) payment method from an account with an identifier (80279F810) to another account (8000A94C0).
* 		2022/09/02 14:36, 022595, 80279F8B0, 0110, 8000A94C0, 5326.79, Australian Dollar, 5326.79, Australian Dollar, ACH, 1: Similarly, this line denotes another transaction on September 2, 2022, with a different amount (5326.79 Australian Dollars) sent via ACH from an account (80279F8B0) to the same account (8000A94C0).
* 		2022/09/03 14:09, 001120, 800E36A50, 0110, 8000A94C0, 4634.81, Australian Dollar, 4634.81, Australian Dollar, ACH, 1: Another transaction occurred on September 3, 2022, involving a distinct amount (4634.81 Australian Dollars) transferred via ACH from a different account (800E36A50) to the same target account (8000A94C0).
* END LAUNDERING ATTEMPT - FAN-IN: Indicates the end of the suspected laundering attempt characterized by a "Fan-In" pattern.
The red flag here is that multiple transactions are directed into the same target account over a short period, possibly attempting to obscure the origin of funds or create a larger amount through aggregation of smaller transactions. This pattern might trigger suspicion of potential money laundering, as it's indicative of trying to funnel multiple smaller amounts into a single account.

Example:2
Gather-scatter.

If the transactions are happening in the following pattern
* 		September 1, 2022:
        * Several transactions occur:
        * Transaction ID 023848: 13573.24 Euros transferred via ACH from account 801A0BEB0 to account 800F963A0.
        * Transaction ID 00498: 3651.60 Euros transferred via ACH from account 8013B3270 to account 800F963A0.
        * Transaction ID 00349: 6980.43 Euros transferred via ACH from account 80049FE00 to account 800F963A0.
* 		September 2, 2022:
        * Multiple transactions continue:
        * Transaction ID 012386: 16003.44 Euros transferred via ACH from account 800F963A0 to account 800F07C90.
        * Transaction ID 01595: 8201.82 Euros transferred via ACH from account 800F963A0 to account 8014DDE40.
        * ...followed by additional transactions involving different currencies and accounts.
* 		September 6, 2022:
    * Transaction ID 022086: 18261.63 US Dollars transferred via ACH from account 800F963A0 to account 800CD0BE0.
The red flag here is the continuous movement of funds within a network of accounts. Funds are gathered into a central account (800F963A0) from various sources and then scattered or distributed across different accounts, often in different currencies, creating a complex web of transactions. This pattern of moving funds between multiple accounts in quick succession could be indicative of attempting to disguise the origin or destination of the funds, a typical characteristic of money laundering through "Gather-Scatter" schemes.

""")
    
    print(prompt.format(data=data))

    #mykey = "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"
    #llm = OpenAI(temperature=0.9,openai_api_key=mykey,model_name='gpt-3.5-turbo')
    #llm = AzureOpenAI(deployment_name="dfp",model_name="gpt-35-turbo")
    llm = AzureChatOpenAI(deployment_name="dfp16k",model_name="gpt-35-turbo-16k")
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Step 7: Run the LLMChain
    output = chain.run(data)
    return output

def query_llm_response1(data):
    prompt = PromptTemplate(
        input_variables=["data"],
        template=""" your task is to identify money laundering transactions and generate reason why such transactions are money laundering with transaction details. In this task, the input is  {data} which contains multiple transactions such as both money laundering and non-money laundering transactions. Each transaction contains multiple attribute such as transaction_id,sender_account_id,transaction_amount,transaction_date,geographical_location,known_customer_locations,receiver_account_id,username,first_name,last_name,full_name,transaction_type,currency.

The reasons should be like if the money transfer from multiple senders to single receiver then give reason multiple sender accounts transfer money to single receiver with detailed explanation. Similarly  if the amount is distributed from single sender account to multiple receiver accounts, then give reason is amount is distributed from single sender to multiple receiver accounts. Similarly for larger sums, and transactions involving multiple currencies. Also indicate sender account details and receiver account details.


Example:
800388YBN,800F963A0,448809.06,14/11/23,UK,USA,800F07C90,ghurtic0,Sayre,Rohlfing,Sayre Rohlfing,ACH,Australian dollar
974129BQ5,800F963A0,109298.1,15/11/23,UK,USA,8014DDE40,rremon1,Mano,Mapledorum,Mano Mapledorum,ACH,Australian dollar
308327ID1,800F963A0,796159.07,16/11/23,UK,UK,800CD0BE0,blanceley2,Roana,Gowry,Roana Gowry,ACH,Australian Dollar
The output should be 
    * Transaction ID 800388YBN: 448809.06 Australian dollar transferred via ACH from sender account 800F963A0 to receiver account 800F07C90.
    * Transaction ID 974129BQ5: 109298.1 Australian dollar transferred via ACH from sender account 800F963A0 to receiver account 8014DDE40.
    * Transaction ID 308327ID1: 796159.07 Australian dollar transferred via ACH from sender account 800F963A0 to receiver account 800CD0BE0.

The identified red flag here is the continuous movement of funds within a network of accounts. Funds are gathered into a central account (e.g., 800F963A0) from various sources and then dispersed across different accounts (e.g., 800F07C90, 8014DDE40, 800CD0BE0), often in different currencies. This complex web of transactions, involving quick succession transfers between multiple accounts. 
 """,
    )
    
    print(prompt.format(data=data))

    #mykey = "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"
    #llm = OpenAI(temperature=0.9,openai_api_key=mykey,model_name='gpt-3.5-turbo')
    #llm = AzureOpenAI(deployment_name="dfp",model_name="gpt-35-turbo")
    llm = AzureChatOpenAI(deployment_name="dfp16k",model_name="gpt-35-turbo-16k")
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Step 7: Run the LLMChain
    output = chain.run(data)
    return output

def extract_transaction_ids(llm_response):
    transaction_ids = re.findall(r"Transaction ID: (\w+)", llm_response) + re.findall(r"Transaction ID (\w+)", llm_response)
    print("Extracted Transaction IDs:", transaction_ids)
    #print("Extracted Transaction IDs:", transaction_ids)
    return transaction_ids

    print(prompt.format(data=data))

    #mykey = "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"
    #llm = OpenAI(temperature=0.9,openai_api_key=mykey,model_name='gpt-3.5-turbo')
    #llm = AzureOpenAI(deployment_name="dfp",model_name="gpt-35-turbo")
    llm = AzureChatOpenAI(deployment_name="dfp16k",model_name="gpt-35-turbo-16k")
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Step 7: Run the LLMChain
    output = chain.run(data)
    return output

def generate_sar_report1(fullnames,firstnames,lastnames,cities,dates,amounts):
    report=" "

    report = f"""FinCEN Form 109
    March, 2011 Previous editions will not be accepted after September 2011
    Suspicious Activity Report by Money Services Business

    Part I
    Subject Information
    *4 Individual’s last name or entity’s full name: {fullnames}
    *5 First name: {firstnames}
     6 Middle initial: NA
    *7 Address: NA
    *8 City: NA
    *9 State: NA
    *10 Zip Code: NA
    *11 Country Code (If not US): {cities}
    *12 Government issued identification (if available): NA
    *13 SSN/ITIN (individual) or EIN (entity): NA
    *14 Date of birth: NA
    15 Telephone number: NA

    Part II
    Suspicious Activity Information
    *16 Date or date range of suspicious activity: {dates}
    *17 Total amount involved in suspicious activity: {amounts}
    *18 Category of suspicious activity: Money Laundering
    *19 Financial services involved in the suspicious activity and character of the suspicious activity: NA
       
    Part III
    Narrative: {langchain_result}
    """
    return report

def fill_pdf(input_pdf_path, output_pdf_path, data_dict):
    pdf = PdfReader(input_pdf_path)
    for page in pdf.pages:
        annotations = page['/Annots']
        if annotations is not None:
            for annotation in annotations:
                if annotation['/Subtype'] == '/Widget':
                    if annotation['/T']:
                        key = annotation['/T'][1:-1]  # Remove parentheses
                        #print(key)
                        if key in data_dict:
                            annotation.update(
                                pdfrw.PdfDict(V='{}'.format(data_dict[key]))
                            )
    PdfWriter().write(output_pdf_path, pdf)

def map_fields(full_names,first_names,last_names,cities,dates,amounts):
     # Map values from input_json to output_json
    dob = f"{random.randint(1950, 2000)}-{random.randint(1, 12)}-{random.randint(1, 28)}"  # Random date of birth
    telephone_number = f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"  # Random phone number
    addresses = ["123 Main St","456 Elm St","789 Oak Ave","567 Pine Rd","890 Maple Blvd"]
    cities_list = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
    states_list = ['NY', 'CA', 'IL', 'TX', 'AZ']
    zip_codes_list = ['10001', '90001', '60601', '77001', '85001']
    ssn_ein_list = [ "SSN123456789","SSN987654321","EIN112233445", "EIN554433221"]
    output_json = {}
    output_json["Text4"] = full_names
    output_json["Text5"] = first_names
    output_json["Text6"] = "NA"
    output_json["Text7"] = random.choice(addresses)
    output_json["Text8"] = random.choice(cities_list)
    output_json["Text9"] = random.choice(states_list)
    output_json["Text10"] = random.choice(zip_codes_list)
    output_json["Text11"] = cities
    output_json["Text12d"] = "NA"
    output_json["Text12e"] = "NA"
    output_json["Text12f"] = random.choice(states_list)
    output_json["Text13"] = ssn_ein_list
    output_json["item14"] = dob
    output_json["Text15"] = telephone_number
    output_json["item16-1"] = dates
    output_json["item16-2"] = dates
    output_json["Text17"] = amounts
    output_json["Text18d-1"] = "NA"
    output_json["Text19d-1"] = "NA"
    output_json["Text24"] = "NA"
    output_json["Text25"] = "NA"
    output_json["Text26"] = "NA"
    output_json["Text27"] = "NA"
    output_json["Text28"] = "NA"
    output_json["Text29"] = "NA"
    output_json["Text30"] = "NA"
    output_json["Text31"] = "NA"
    output_json["Text32"] = "NA"
    output_json["Text33"] = "NA"
    output_json["Text35"] = "NA"
    output_json["Text36"] = "NA"
    output_json["Text37"] = "NA"
    output_json["Text38"] = "NA"
    output_json["Text39"] = "NA"
    output_json["Text40"] = "NA"
    output_json["Text41"] = "NA"
    output_json["Text42"] = "NA"
    output_json["Text43"] = "NA"
    output_json["Text44"] = "NA"
    output_json["Text45"] = "NA"
    output_json["Text46"] = "NA"
    output_json["item47"] = "NA"
    output_json["Text48"] = "FBI"  # Assuming FBI as the agency for reporting

    return output_json




# Streamlit app
st.title("SAR Report Generator for Money Laundering")

# Load your data
df=pd.read_csv("/Users/centific/Downloads/Email Generator App - Source Code/MOCK_DATA.csv")
#df=df.drop(columns=['label','geographical_location','known_customer_locations','username'])
df1=df
df=df.drop(columns=["label"])
#df=df[:50]

# Select a column for the pie chart (e.g., 'geographical_location')
selected_column = st.selectbox("Select a column for the pie chart:", df1.columns)

# Create a pie chart
fig, ax = plt.subplots()
df1[selected_column].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=plt.cm.Paired.colors)
ax.set_aspect('equal')  # Equal aspect ratio ensures that the pie is drawn as a circle.

# Display the pie chart using Streamlit
st.pyplot(fig)

df['Total Amount']=df['transaction_amount']
df.rename(columns = {'geographical_location':'city', 'username':'Name','transaction_amount':'t_amount'}, inplace = True)
#data1=df.to_dict(orient='records')
st.write(df.head())

langchain_result = query_llm_response1(df)
# Get LangChain response
if st.button("Process Transactions"):
    st.write("Response:")
    st.write(langchain_result)

extracted_ids = extract_transaction_ids(langchain_result)
#langchain_result1 = query_llm_response1(langchain_result)
#full_names = #
#first_names=
#last_names=
#cities = 
#dates = 
#amounts =

# Iterate through each transaction ID and extract corresponding attribute values
for transaction_id in extracted_ids:
    # Filter the data for a specific transaction ID
    output_pdf_path = f'output_{transaction_id}.pdf'
    if transaction_id in list(df['transaction_id']):
       data_for_id = df[df['transaction_id'] == transaction_id]
       full_names=data_for_id['full_name'].values[0]
       first_names=data_for_id['first_name'].values[0]
       last_names=data_for_id['last_name'].values[0]
       cities=data_for_id['city'].values[0]
       dates=data_for_id['transaction_date'].values[0]
       amounts=data_for_id['Total Amount'].values[0]
    else:
        #df.loc[row_number, columns_of_interest]
        full_names=df.loc[transaction_id, ['full_name']]
        first_names=df.loc[transaction_id, ['first_name']]
        last_names=df.loc[transaction_id, ['last_name']]
        cities=df.loc[transaction_id, ['city']]
        dates=df.loc[transaction_id, ['transaction_date']]
        amounts=df.loc[transaction_id, ['Total Amount']]
    output_json = map_fields(full_names,first_names,last_names,cities,dates,amounts)
    fill_pdf('SAR-template.pdf', output_pdf_path, output_json)
    

#if st.button("Extract money laundering transactionid"):
    #st.write("LangChain Response:")
    #st.write(extracted_ids)
 
sar_report = generate_sar_report1(full_names,first_names,last_names,cities,dates,amounts)
#if st.button("Generate SAR Report"):
   
    #sar_report = generate_sar_report1(names,cities,dates,amounts)
    #dataextractlist = extractfn(sar_report,df)
    #st.write("Generated SAR Report:")
    #sar_report1.append(sar_report)
    #st.write(sar_report)
tab1, tab2,tab3 = st.tabs(["Suscipicious Transactions", " Transaction Id", "SAR Report"])
tab1.write(langchain_result)
tab2.write(extracted_ids)
tab3.write(sar_report)
