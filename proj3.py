import pymongo
import argparse
import sys
import os
import datetime as dt
import xlsxwriter
import subprocess
import shlex
from sys import stdout


myclient = pymongo.MongoClient("mongoDBlink")
mydb = myclient["mycollections"]
mycolMeta = mydb["meta"]
mycolLoc = mydb["locFile"]

# delete_col = mycolMeta.delete_many({})
# delete_col = mycolLoc.delete_many({}) 

print(sys.argv)

parser = argparse.ArgumentParser()

parser.add_argument("--files", dest="workFiles", nargs="+", help="files to process")
parser.add_argument("--Xytech", dest="x_files", help="files to process")
parser.add_argument("--verbose", action="store_true", help="show verbose")
parser.add_argument("--output", dest="output", help="output Choice")
parser.add_argument("--process", dest="thumbnails", help="grabbing thumbnails from ffmpeg") # need to connect to it 
args = parser.parse_args()
#print(args.workFiles)
if args.workFiles is None:
    print("No BL/Flames files selected")
    sys.exit(2)
else:
    job = args.workFiles
    if args.verbose: 
        print("verbose!")    


def frame_to_timecode(input): # frame to time code function. Used from weekly lesson 7 and changed it to / 60
    #print("INPUT:", input)
    if int(input) < 60:
        return "{:02d}:{:02d}:{:02d}.{:02d}".format(0,0,0 , int(input)) # 00:00:00.00
    totalSeconds = int(input) / 60 # division
    #print(totalSeconds, "total seconds")
    hours = int(totalSeconds / 3600)
    #print(hours, "hours")
    minutes = int((totalSeconds % 3600) / 60)
    #print(minutes, "minutes")
    seconds = int(totalSeconds % 60)
    #print(seconds, "seconds")
    nanoseconds = int(input) % 60 # remainder
    #print("*******")
    return "{:02d}:{:02d}:{:02d}.{:02d}".format(hours, minutes, seconds, nanoseconds)

import csv

#Open Xytech file
xytech_file_location = args.x_files
xytech_folders = []

read_xytech_file = open('./import_files/' + xytech_file_location, "r")
for line in read_xytech_file:
    if "/" in line:
        xytech_folders.append(line)

file_locations = []
file_metadata = []

#Open Baselight file
for file in args.workFiles:
    #print(file)
    baselight_file_location = file
    read_baselight_file = open('./import_files/' + baselight_file_location, "r")

    baselight_file_location = baselight_file_location.split("_")
    nameOfMachine = baselight_file_location[0]
    # print(nameOfMachine)
    # print(os.getlogin())
    file_metadata.append({
        "nameofUser":os.getlogin(),
        "nameofMachine":nameOfMachine,
        "nameOfUserOnFile":baselight_file_location[1], 
        "dateofFile":baselight_file_location[-1][:-4],
        "submittedDate":dt.datetime.now()
    })
    #print(file_metadata)
    #Read each line from Baselight file
    for line in read_baselight_file:
        line_parse = line.split(" ")
        current_folder = ""
        if "flame" in line_parse[0]:
            current_folder = line_parse.pop(0) + " " + line_parse.pop(0)
        else:
            current_folder = line_parse.pop(0)
        #print(current_folder)
        sub_folder = current_folder.replace("/images1/Avatar", "").replace("/net/flame-archive Avatar", "") # handle flame files here as well
        new_location = ""
        #Folder replace check
        for xytech_line in xytech_folders:
            if sub_folder in xytech_line:
                new_location = xytech_line.strip()
        #print(xytech_folders)
        first=""
        pointer=""
        last=""
        print("NEW LOCATION", new_location)
        for numeral in line_parse:
            #Skip <err> and <null>
            if not numeral.strip().isnumeric():
                continue
            #Assign first number
            if first == "":
                first = int(numeral)
                pointer = first
                continue
            #Keeping to range if succession
            if int(numeral) == (pointer+1):
                pointer = int(numeral)
                continue
            else:
                #Range ends or no sucession, output
                last = pointer
                if first == last:
                    file_locations.append({"user":baselight_file_location[1], "date":baselight_file_location[-1][:-4], "location":new_location, "range":first, "timecode":frame_to_timecode(first)})
                else:
                    file_locations.append({"user":baselight_file_location[1], "date":baselight_file_location[-1][:-4], "location":new_location, "range":str(first) + "-" + str(last),"timecode":frame_to_timecode(first) + "-" + frame_to_timecode(last)})
                first= int(numeral)
                pointer=first
                last=""
        #Working with last number each line 
        last = pointer
        if first != "":
            if first == last:
                file_locations.append({"user":baselight_file_location[1], "date":baselight_file_location[-1][:-4], "location":new_location, "range":first, "timecode":frame_to_timecode(first)})
            else:
                file_locations.append({"user":baselight_file_location[1], "date":baselight_file_location[-1][:-4], "location":new_location, "range":str(first) + "-" + str(last), "timecode":frame_to_timecode(first) + "-" + frame_to_timecode(last)})
if args.verbose:
    print(file_locations)
    print(file_metadata)

# databaseCall1 = mycolLoc.find({"user": "TDanza"}) # proj2
# for row in databaseCall1:
#     print("Database Collection 1: ", row)

# print("*******")

# databaseCall2 = mycolLoc.find({"date": {"$lte": "20230325"}, "user": {"$in": ["MFelix","DFlowers"]}}) #proj2
# for row2 in databaseCall2:
#     print("Database Collection 2: ", row2)

# print("*******")

# databaseCall3 = mycolLoc.find({"location": {"$regex": 'hpsans13'}, "date": "20230326"}) # proj2
# for row3 in databaseCall3:
#     print("Database Collection 3:", row3)   
# else:
#     print("Database Collection 3: No Value found")     

# print("*******")

# databaseCall4 = mycolLoc.find({"user": {"$in": ["MFelix","DFlowers"]}}) #proj2
# for row4 in databaseCall4:
#     print("Database Collection 4:", row4["user"])  

# proj 3

inputFile = "twitch_nft_demo.mp4"




# print(result)

if args.thumbnails == "twitch_nft_demo.mp4":

    databaseProj3 = mycolLoc.find({"range":{"$lte": "6000"}})

    if args.output == "xls":
        workbook = xlsxwriter.Workbook("proj3.xlsx")
        worksheet = workbook.add_worksheet()
        worksheet.set_column("A:A", 49)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 25)
        worksheet.set_column("D:D", 20)
        worksheet.set_default_row(60) 
        for idx,loc in enumerate(databaseProj3):
            try:
                if int(loc["range"].split("-")[1]) <= 6000:
                    worksheet.write(idx,0,loc["location"])
                    worksheet.write(idx,1,loc["range"])
                    first = frame_to_timecode(loc["range"].split("-")[0])
                    last = frame_to_timecode(loc["range"].split("-")[1])
                    worksheet.write(idx,2,str(first) + "-" + str(last))
                    print("hello")
                    add = int(loc["range"].split("-")[0]) + int(loc["range"].split("-")[1])
                    midTimeCode = frame_to_timecode(add / 2)
                    print(midTimeCode)
                    ffmpegCom = f'ffmpeg -i {inputFile} -s 96x74 -ss {midTimeCode} -vframes 1 thumbnail{idx}.png' # in -ss should be the middle frame of the timecodes

                    

                    var = shlex.split(ffmpegCom)
                    result = subprocess.run(var, shell=False, stdout=subprocess.PIPE)

                    
                    worksheet.insert_image(idx,3,f'thumbnail{idx}.png')
                #print("DATABASE PROJ 3", loc)
            except:
                print("shant")
        workbook.close()
    elif args.output == "csv":
        with open("proj2export.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(file_locations[0].keys())
            for row in file_locations:
                writer.writerow(row.values())
    else:
        mycolLoc.insert_many(file_locations)
        mycolMeta.insert_many(file_metadata)


# 1. <User that ran script> <Machine> <Name of User on file> <Date of file> <submitted date>
# 2. <Name of User on file> <Date of file> <location> <frame/ranges>
