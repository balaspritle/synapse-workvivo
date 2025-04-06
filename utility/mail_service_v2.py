import utility.config as config
import sendgrid, os, base64, time, shutil, datetime, pytz
from dateutil import parser
from sendgrid.helpers.mail import *
import utility.aws as aws
import utility.workvivo as fb_workplace
import pandas as pd
import numpy as np
from dateutil import tz
from collections import Counter
import concurrent.futures    
import utility.db_utils as db_utils
from utility.azure_log_analytics import query_log_analytics


pd.options.mode.chained_assignment = None
file_type = {'.pdf': 'application/pdf', '.xlsx': 'application/xlsx', '.xls': 'application/xls', '.docx': 'application/docx'}
fmt = "%Y-%m-%d %H:%M:%S%z"
sgt_timezone = pytz.timezone('Asia/Singapore')

# SendGrid Mail Sender
def sendEmail(subject, content):
    # print("Sending an email", subject, content)
    for sender_email_ in config.sender_email:
        print("sender_email_", sender_email_)
        try:
            sg = sendgrid.SendGridAPIClient(api_key=config.SENDGRID_API_KEY)
            from_email = Email("do-not-reply@zevigosolutions.com")
            to_email = To(sender_email_)
            mail = Mail(from_email, to_email, subject, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            print("sendEmail", response.status_code) #, response.body, response.headers)
            return True
        except Exception as e:
            print(e)
            return False

def send_Failsafe_Email(subject, content):
    for sender_email_ in ["nans.sgp@gmail.com","praveen.r@spritle.com","balakrishnav@spritle.com"]:
        try:
            sg = sendgrid.SendGridAPIClient(api_key=config.SENDGRID_API_KEY)
            from_email = Email("do-not-reply@zevigosolutions.com")
            to_email = To(sender_email_)
            mail = Mail(from_email, to_email, subject, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            print("sendEmail", response.status_code) #, response.body, response.headers)
            return True
        except Exception as e:
            print(e)
            return False
    
def sendEmailWithAttachment(user_data, attachment_id):
    # print(user_data, attachment_id, "user_data & attachment_id")
    try:   
        file_type = {'.pdf': 'application/pdf', '.xlsx': 'application/xlsx', '.xls': 'application/xls', '.docx': 'application/docx'}
        query = "SELECT s3_uri FROM artefacts WHERE attachment_id = %s"
        argument = ("b" + str(attachment_id))
        row = db_utils.read_data_from_db(query, argument)
        
        if row:
            s3_uri = row[0][0]
        else:
            print("Unable to find the document in the database", attachment_id)
            return
        attachment_filepath = aws.download_from_s3(s3_uri)
        with open(attachment_filepath, 'rb') as f:
            data = f.read()
            f.close()
        encoded_file = base64.b64encode(data).decode()

        attachedFile = Attachment(
            FileContent(encoded_file),
            FileName(os.path.basename(attachment_filepath)),
            FileType(file_type[os.path.splitext(attachment_filepath)[-1]]),
            Disposition('attachment')
        )
        
        text = ""
        text += "Dear {} <br>".format(user_data['name'])
        text += "<br> You are receiving this email because you have made a request through the HCM Chatbot on Workplace to receive a form : {} <br>".format(os.path.basename(attachment_filepath))
        text += "<br> If this is not the form you are looking for, please try again on the HCM Chatbot.<br>"
        text += "<br> We wish you a good day ahead! <br><br>"
        text += "<strong> NOTE: This is an IHIS HCM Chatbot system-generated email. </strong>"
        message = Mail(
            from_email = 'do-not-reply@zevigosolutions.com',
            to_emails = user_data['email'],
            subject = "HCM Chatbot Emails to Staff",
            html_content =  text
        )
        message.attachment = attachedFile

        sg = sendgrid.SendGridAPIClient(config.SENDGRID_API_KEY)
        response = sg.send(message)
        print("sendEmailWithAttachment", response.status_code) #, response.body, response.headers)
        
        try:
            time.sleep(5)
            shutil.rmtree(os.path.dirname(attachment_filepath))
        except FileNotFoundError:
            pass

        timestamp = str(datetime.datetime.strftime(datetime.datetime.now(pytz.timezone('Asia/Singapore')), "%Y-%m-%d %H:%M:%S"))
        query = "INSERT INTO email_with_attachment_logs (date, time, user_id, attachment_id, filename) VALUES (%s, %s, %s, %s, %s)"
        argument = (str(parser.parse(timestamp).date()), str(parser.parse(timestamp).time()), user_data['id'], str(attachment_id), str(os.path.basename(attachment_filepath)))
        db_utils.insert_data_to_db(query, argument)
        
    except Exception as e:
        print("Error in sendEmailWithAttachment", e)                        


def db_filtering(duration, table_name):
    print("Triggered {} for a duration of {} days".format(table_name, duration))
    
    if(type(duration) is tuple):
        start_date = duration[0]
        end_date = duration[-1] + datetime.timedelta(days = 1)
    else:
        start_date = (pd.Timestamp.today() - pd.Timedelta('{}D'.format(duration))).date()
        end_date = (pd.Timestamp.today() + pd.Timedelta('1D')).date()
    
    try:
        query = "select * from {} where date >= '{}' AND date <= '{}'".format(table_name, start_date, end_date)
        df = db_utils.read_data_from_db_as_df(query)
        return df
    except Exception as e:
        print("Error in {}".format(table_name), e)
        return pd.DataFrame()

def get_user_email(row, user_id_to_email_mapper):
    # user_id_variants = ['UserId', 'user_id', 'UserId', 'Unique User_Id']
    # try:
    #     for user_id_variant in user_id_variants:
    try:
        return user_id_to_email_mapper[str(row['user_id'])]
    except Exception as e:
        print("Error in get_user_email", str(e), row)
        return "N/A"
    

def utc_to_sgt(row):
    timestamp = str(row['timestamp'])
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Singapore')

    utc = datetime.datetime.strptime(timestamp, fmt)
    utc = utc.replace(tzinfo=from_zone)

    sgt = utc.astimezone(to_zone)
    return str(sgt).split('.')[0], str(sgt.date()), str(sgt.time()).split('.')[0]
    
def chatlog_formatter(df, user_id_to_email_mapper):
    user_id_to_remove = [100078065712033, "Default", "100078065712033"]
    ignore_phrases = ["DIAYQ-YES", "ZEVIGOSOLUTIONSSEY", "ZEVIGOSOLUTIONSON", "Hi", "hi", "1.Power", "2.Nubaad", "3.Okay", "4.Cannot make it"]
    
    df = df.drop(labels=['KbId'], axis=1)

    try:
        df["Timestamp SGT"], df["date"], df['Time'] = zip(*df.apply(utc_to_sgt, axis=1))
    except ValueError:
        df["Timestamp SGT"], df["date"], df['Time'] = None, None, None
    df = df.drop(labels=['timestamp'], axis=1)
    df = df[['date', 'Time', 'user_id', 'question', 'answer', 'score']]
    df = df[~df.user_id.isin(user_id_to_remove)]
    df = df[~df.question.isin(ignore_phrases)]
    df['User Email'] = df.apply(get_user_email, user_id_to_email_mapper = user_id_to_email_mapper, axis = 1)
    return df 

def extract_time(row):
    return str(row).split('days')[-1].strip()

def add_cache_data(df_cleaned, user_id_to_email_mapper, duration):
    df = db_filtering(duration, "user_cache_logs")
    
    df['Time'] = df.time.apply(extract_time)

    user_id_to_remove = [100078065712033, "Default", "100078065712033"]
    ignore_phrases = ["DIAYQ-YES", "ZEVIGOSOLUTIONSSEY", "ZEVIGOSOLUTIONSON", "Hi", "hi", "1.Power", "2.Nubaad", "3.Okay", "4.Cannot make it"]

    df = df[~df.user_id.isin(user_id_to_remove)]
    df = df[~df.question.isin(ignore_phrases)]
    
    def add_cache_to_df(row, df_dict):
        holder = next((item for item in df_dict if item["question"] == row['question']), None)
        if holder:
            return pd.Series(list(holder.values())[4:-1])
        return pd.Series([None, None, None, None])
        
    df_dict = df_cleaned.to_dict(orient="records")
    
    df[['answer', 'score', 'duration', 'performanceBucket']] = df.apply(add_cache_to_df, df_dict = df_dict, axis = 1)
    df['User Email'] = df.apply(get_user_email, user_id_to_email_mapper = user_id_to_email_mapper, axis = 1)
    
    ## Clean
    df = df.replace('', np.nan)
    df = df.dropna()

    df = pd.concat([df_cleaned, df], ignore_index=True)
    df['date'] = df['date'].astype(str)
    df['user_id'] = df['user_id'].astype(str)
    return df

    
def sendWeeklyChatLogs(duration, user_id_to_email_mapper):
    print("Triggered sendWeeklyChatLogs for a duration of {} days".format(duration))
    
    if isinstance(duration, tuple):
        start_date = datetime.datetime.combine(duration[0], datetime.time.min, tzinfo=pytz.utc).astimezone(sgt_timezone)
        end_date_original = datetime.datetime.combine(duration[-1], datetime.time.min, tzinfo=pytz.utc).astimezone(sgt_timezone)
        end_date = end_date_original + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
    else:
        today = datetime.datetime.now(pytz.utc).astimezone(sgt_timezone).date()
        start_date = datetime.datetime.combine(today - datetime.timedelta(days=duration), datetime.time.min, tzinfo=sgt_timezone)
        end_date_original = datetime.datetime.combine(today, datetime.time.min, tzinfo=sgt_timezone)
        end_date = end_date_original + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
        
    timespan = (start_date, end_date)
    timespan_original = "{}/{}".format(start_date.date(), end_date_original.date())
    
    try:    
        # params = {"query": config.query, "timespan": timespan}
        # headers = {'X-Api-Key': config.appKey}
        # url = f'https://api.applicationinsights.io/v1/apps/{config.appId}/query'

        # response = requests.get(url, headers=headers, params=params)
        # logs = json.loads(response.text)
        # df = pd.DataFrame(logs['tables'][0]['rows'], columns =['timestamp', 'resultCode', 'duration', 'user_id', 'question', 'answer', 'score', 'performanceBucket', 'KbId'])
        
        df = query_log_analytics(timespan)
        df = df.replace('', np.nan)
        df = df.dropna()
        df_cleaned = chatlog_formatter(df, user_id_to_email_mapper)
        
        try:
            df_cleaned = add_cache_data(df_cleaned, user_id_to_email_mapper, duration)
        except Exception as e:
            print("Error in add_cache_data", e)            
        
        return df_cleaned, df, timespan_original
    except Exception as e:
        print("Error in sendWeeklyChatLogs", e)
        send_Failsafe_Email("Some Issue in Sending Weekly Logs to Synapse LTD", "Error Message is : " + str(e))
        return None
    
def shoot_email(attachment_filepath):
    try:
        with open(attachment_filepath, 'rb') as f:
            data = f.read()
            f.close()
        encoded_file = base64.b64encode(data).decode()
        attachedFile = Attachment(FileContent(encoded_file), FileName(os.path.basename(attachment_filepath)), FileType(file_type[os.path.splitext(attachment_filepath)[-1]]), Disposition('attachment'))
        text = ""
        text += "To HR <br>"
        text += "<br>This mail contains the complete logs based on Iris Bot usage.<br>"
        text += "We wish you a good day ahead! <br><br>"
        text += "PFA"
        
        sg = sendgrid.SendGridAPIClient(config.SENDGRID_API_KEY)
        
        for sender_email_ in config.sender_email:
            print("sender_email_", sender_email_)
            message = Mail(
                from_email = 'do-not-reply@zevigosolutions.com',
                to_emails = sender_email_,
                subject = "Iris Bot - Complete Logs (Custom Question Answering)",
                html_content =  text
            )
            message.attachment = attachedFile

            response = sg.send(message)
            print("sendEmailWithAttachment", response.status_code, sender_email_) #, response.body, response.headers)
            
        try:
            time.sleep(5)
            os.remove(attachment_filepath)
        except FileNotFoundError:
            pass
    except Exception as e:
        print("Error in shoot_email", e)

# sendEmailWithAttachment({'name': 'balakrishnav', 'id': '100077347014829', 'email': 'balakrishnav@spritle.com'}, 1121668335291338)

def func_graph_1(df):
    ## Graph - 1 - Number of queries received
    df1_graph_1 = pd.DataFrame(sorted(dict(Counter(df.date)).items()), columns=['date', 'Number of queries'])
    df1_graph_1 = df1_graph_1[['date', 'Number of queries']]
    return df1_graph_1
    
def func_graph_2(df):
    ## Graph - 2 - Unique users
    holder = [(tuple([date_, len(pd.unique(df[df.date == date_]['user_id'])), len(df[df.date == date_]['user_id'])])) for date_ in sorted(pd.unique(df.date))]
    df1_graph_2 = pd.DataFrame(holder, columns=['date', 'Number of unique users who used chatbot', 'Total Queries'])
    df1_graph_2['Average Queries per User'] = df1_graph_2['Total Queries'] / df1_graph_2['Number of unique users who used chatbot']
    try:
        df1_graph_2['Average Queries per User'] = df1_graph_2.apply(lambda x: int(x['Average Queries per User']),axis=1)
    except ValueError:
        df1_graph_2['Average Queries per User'], df1_graph_2['date'] = None, None
    df1_graph_2 = df1_graph_2[['date', 'Number of unique users who used chatbot', 'Total Queries', 'Average Queries per User']]
    return df1_graph_2
        
def func_graph_3(df, user_id_to_email_mapper):
    ## Graph - 3 - List of Unique Users

    holder = []
    for date_ in sorted(pd.unique(df.date)):
        for user_id_ in list(pd.unique(df[df['date'] == date_]['user_id'])):
            holder.append(tuple([date_, user_id_, df[(df.date == date_) & (df.user_id == user_id_)].shape[0]])) 
            
    df1_graph_3 = pd.DataFrame(holder, columns=['date', 'user_id', 'Count of queries by Users'])
    df1_graph_3['User Email'] =  df1_graph_3.apply(get_user_email, user_id_to_email_mapper = user_id_to_email_mapper, axis = 1)
    df1_graph_3 = df1_graph_3[['date', 'user_id', 'User Email', 'Count of queries by Users']]
    return df1_graph_3

def func_graph_4(df):
    ## Graph - 4 - Scores Distribution
    holder = []
    try:
        df['score'] = df.apply(lambda x: float(x['score']),axis=1)
    except ValueError:
        df['score'] = None
    holder.append(tuple(["65 to 100",    len(df[df['score'] >= float(config.score_threshold)])]))
    holder.append(tuple(["64 and below", len(df[df['score'] < float(config.score_threshold)])]))
    df1_graph_4 = pd.DataFrame(holder, columns=['SCORE', 'No. of Queries'])   
    return df1_graph_4 
    
def func_graph_5(df3):
    ## Graph - 5 - df3 postprocessing
    holder = [(tuple([date_, len(df3[df3['date'] == date_])])) for date_ in sorted(pd.unique(df3['date']))]
    df3 = pd.DataFrame(holder, columns=['date', 'Number of eligible queries'])   
    return df3 

def func_graph_6(df4):
    ## Graph - 6
    holder = [(tuple([date_, len(df4[df4['date'] == date_])])) for date_ in sorted(pd.unique(df4['date']))]
    df4 = pd.DataFrame(holder, columns=['date', 'Number of eligible queries'])  
    return df4
    
def func_graph_8(df2, user_id_to_email_mapper):
    ## Graph - 8 - df2 postprocessing
    try:
        df2['Feedback date'] = df2.date
        df2['User Email'] =  df2.apply(get_user_email, user_id_to_email_mapper = user_id_to_email_mapper, axis = 1)
        df2['Feedback text'] = df2.comments
        df2['Rating given'] = df2.rating
    except ValueError:
        df2['Feedback date'], df2['User Email'], df2['Feedback text'], df2['Rating given'] = None, None, None, None
    df2 = df2[['Feedback date', 'User Email', 'Feedback text', 'Rating given']]
    return df2 

def func_graph_9(df):
    ## Graph - 9 - Top 10 asked queries
    holder = [(tuple([i[0], i[1]])) for i in Counter(df.question.tolist()).most_common(100) if int(i[1]) >= 2]
    df9 = pd.DataFrame(holder, columns=['Question', 'Number of times asked'])
    return df9
    
def func_graph_10(df, user_id_to_email_mapper):
    ## Graph - 10 - df
    if df.empty:
        print("Empty DataFrame")
        df['User Email'] = None
        return df
    else:
        df['time'] = df.time.apply(extract_time)
        try:
            df['User Email'] =  df.apply(get_user_email, user_id_to_email_mapper = user_id_to_email_mapper, axis = 1)
        except ValueError:
            df['User Email'] = None
        return df 

def consolidated_analytics(duration):
    # duration format --> tuple([datetime.datetime.strptime('2022-01-01', '%Y-%m-%d').date(), (datetime.datetime.strptime('2022-06-10', '%Y-%m-%d') + datetime.timedelta(days=1)).date()])
    print("consolidated_analytics duration -", duration)
    
    all_fb_users = fb_workplace.all_users #get_all_user_id()
    user_id_to_email_mapper = {}
    for user in all_fb_users:
        if user.get('email'):
            user_id_to_email_mapper[user['id']] = user['email']
    
    ## Constants
    df1, df1_uncleaned, timespan = sendWeeklyChatLogs(duration=duration, user_id_to_email_mapper=user_id_to_email_mapper)
    df2 = db_filtering(duration, "user_comments")
    df3 = db_filtering(duration, "user_escalations")
    df4 = db_filtering(duration, "user_not_satisfied")
    df5 = db_filtering(duration, "game_reports")

    ## Graph - 1 - Number of queries received
    df1_graph_1 = func_graph_1(df1) 

    ## Graph - 2 - Unique users
    df1_graph_2 = func_graph_2(df1)

    ## Graph - 3 - List of Unique Users
    df1_graph_3 = func_graph_3(df1, user_id_to_email_mapper)

    ## Graph - 4 - Scores Distribution
    df1_graph_4 = func_graph_4(df1)    

    # df1_uncleaned = df1_uncleaned[df1_uncleaned['question'] == "DIAYQ-YES"]
    # holder = {}
    # for date_ in pd.unique(df1_uncleaned.Date):
    #     holder[date_] = len(pd.unique(df1_uncleaned[df1_uncleaned.Date == date_]['UserId']))
    # df1_graph_3 = pd.DataFrame(sorted(dict(holder).items()), columns=['Date', 'Number of queries resolved'])
    # df1_graph_3['Date'] = df1_graph_3.apply(date_formatter, axis = 1)

    ## Graph - 5 - df4 postprocessing
    # df4['User Email'] = df4.apply(get_user_email, user_id_to_email_mapper = user_id_to_email_mapper, axis = 1)
    # df4['Message Content'] = df4['Message Content'].apply(lambda x: "No" if x == "DIAYQ-NO" else x)
    # df4 = df4[['Date', 'User Id', 'User Email', 'Message Content']]
    
    ## Graph - 5 - df3 postprocessing 
    df3 = func_graph_5(df3)    

    ## Graph - 6
    df4 = func_graph_6(df4)  

    ## Graph - 7 - df1 as it is
    df1 = df1[['date', 'Time', 'user_id', 'User Email', 'question', 'answer', 'score']]

    ## Graph - 8 - df2 postprocessing
    df2 = func_graph_8(df2, user_id_to_email_mapper)
    
        
    ## Graph - 9 - Top 10 asked queries
    df9 = func_graph_9(df1)

    ## Graph - 10 - Game Reports
    df5 = func_graph_10(df5, user_id_to_email_mapper)

    ## Returning users
    # holder = []
    # for user_id_ in pd.unique(df1.UserId):
    #     holder.append(tuple([user_id_, df1[df1['UserId'] == user_id_]['User Email'].values[0], df1[df1['UserId'] == user_id_].shape[0], df1_uncleaned[(df1_uncleaned['UserId'] == user_id_) & (df1_uncleaned['question'] == "DIAYQ-YES") ].shape[0] ]))
    # df9 = pd.DataFrame(holder, columns=['User ID', 'User Email', 'how many times transacted within the month',	'how many queries resolved'])  
    
    try:
        final_df_file_name = "consolidated analytics {} to {}.xlsx".format(str(timespan.split('/')[0]), str(timespan.split('/')[-1]))
    except:
        final_df_file_name = "consolidated analytics_no_data_available.xlsx"
        
    attachment_filepath = os.path.join( os.path.dirname(os.path.join(os.getcwd(), config.cache_path)), final_df_file_name)
    print("attachment_filepath", attachment_filepath)
    
    with pd.ExcelWriter(attachment_filepath) as writer:
        df1_graph_1.to_excel(writer, sheet_name='Number of queries received',index=False)
        df1_graph_2.to_excel(writer, sheet_name='No of Unique Users',index=False)
        df1_graph_3.to_excel(writer, sheet_name='List of Unique Users',index=False)
        df1_graph_4.to_excel(writer, sheet_name='Score of the queries',index=False)
        
        df3.to_excel(writer, sheet_name='Total Number of Escalations',index=False)
        df4.to_excel(writer, sheet_name='No of queries not understood',index=False)
        
        df1.to_excel(writer, sheet_name='Conversation log',index=False)
        df2.to_excel(writer, sheet_name='Feedback survey',index=False)
        df9.to_excel(writer, sheet_name='Top 10 Questions',index=False)
        df5.to_excel(writer, sheet_name='Game Reports',index=False)

    shoot_email(attachment_filepath)
    user_id_to_email_mapper.clear()

def all_weekly_mails(duration = 7):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = executor.map(consolidated_analytics, [duration,])
        
# scheduler = BackgroundScheduler(timezone=config.timezone)
# scheduler.start()

# scheduler.add_job(
#     all_weekly_mails,
#     'cron',
#     day_of_week=config.day_of_the_week, 
#     hour=config.hour, 
#     minute=config.minute
# )