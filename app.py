import os
from dotenv import load_dotenv
from flask import Flask, render_template
from forms import CSVForm
from datetime import datetime
import pandas as pd

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
admins = os.getenv("NAMES").split(",")

@app.route("/", methods=["GET", "POST"])
def index():
    form = CSVForm()

    if form.validate_on_submit():
        if form.csv.data:
            df = pd.read_csv(form.csv.data)
            
            for admin in admins:
                df = df[df["User full name"] != admin]
            ip_counts = df.groupby("User full name")["IP address"].nunique()
            names = ip_counts[ip_counts > 1]
            
            details = {
                "name" : [],
                "ip" : [],
                "start" : [],
                "finish" : [],
                "duration" : []
            }
            for name, group_df in df.groupby("User full name"):
                unique_ips = group_df["IP address"].unique()
                student = {}
                if name in names:
                    student["name"] = name
                    for ip in unique_ips:
                        if ip not in details["ip"] :
                            df_us = df[df["User full name"] == name]
                            df_ip =  df_us[df_us["IP address"] == ip]
                            student[f"ip"] = ip
                            ip_time_ranges = df_ip.groupby("IP address")["Time"].agg(["min", "max"])
                            ip_time_ranges = dict(ip_time_ranges)
                            student[f"range"] = {
                                "min" : str(list(ip_time_ranges["min"])).strip("''[]"),
                                "max" : str(list(ip_time_ranges["max"])).strip("''[]")
                            }
                            details["name"].append(student["name"])
                            details["ip"].append(student["ip"])
                            details["start"].append(student["range"]["min"])
                            details["finish"].append(student["range"]["max"])
                            details["duration"].append(datetime.strptime(student["range"]["max"], '%d/%m/%y, %H:%M:%S') - datetime.strptime(student["range"]["min"], '%d/%m/%y, %H:%M:%S'))

            result_df = pd.DataFrame(details)

            ips = result_df["ip"]
            # for ip in result_df["ip"]:
            #     users = df[df["IP address"] == ip]
            filtered_df = df[df['IP address'].isin(ips)]
            grouped = filtered_df.groupby('IP address')['User full name'].unique().reset_index()
            grouped["User full name"] = grouped["User full name"].apply(list)
            # print(grouped)

            details = {
                "ip" : [],
                "name" : [],
                "start" : [],
                "finish" : [],
                "duration" : []
            }

            for index, users in enumerate(grouped["User full name"]):
                # print(index, grouped["IP address"][index])
                for user in users:
                    # print(user, end=" ")
                    df_us = df[df["User full name"] == user]
                    df_ip =  df_us[df_us["IP address"] == grouped["IP address"][index] ]
                    user_time_ranges = df_ip.groupby("User full name")["Time"].agg(["min", "max"])
                    user_time_ranges = dict(user_time_ranges)
                    details["ip"].append(grouped["IP address"][index])
                    details["name"].append(user)
                    min = str(list(user_time_ranges["min"])).strip("''[]")
                    details["start"].append(min)
                    max = str(list(user_time_ranges["max"])).strip("''[]")
                    details["finish"].append(max)
                    details["duration"].append(datetime.strptime(max, '%d/%m/%y, %H:%M:%S') - datetime.strptime(min, '%d/%m/%y, %H:%M:%S'))
                    

            analysis_df = pd.DataFrame(details)

            analysis_df['start'] = pd.to_datetime(analysis_df['start'], format='%y/%m/%d, %H:%M:%S')
            analysis_df = analysis_df.sort_values(by=['ip', 'start'])
            analysis_df = analysis_df.reset_index()
            analysis_df = analysis_df.drop(columns=["index"])

            result = result_df.to_html(classes='table table-striped table-bordered')
            analysis = analysis_df.to_html(classes='table table-striped table-bordered')

            return render_template("index.html", form=form, result=result, analysis=analysis)

    return render_template("index.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)