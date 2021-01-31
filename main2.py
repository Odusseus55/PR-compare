from flask import Flask, render_template, request, send_file, flash, redirect, request, url_for
import pandas as pd
import itertools


# PRdesc_rows_list = []

def sort_PR(x):
        my_list = x.split("+")
        my_list = sorted(my_list, key=str.lower)
        my_string = '+'.join(my_list)
        #print(my_string)
        return my_string

def doubleslash_separator(x, y=0):

    if '//' in y:
        PR_desc_split = y.split('//')

        y = PR_desc_split[0]
        del PR_desc_split[0]

        for i in PR_desc_split:
            dict_add = {'PartNumber': x, 'PR': i}
            PRdesc_rows_list.append(dict_add) 

        #print('RRdescrowlist: ', PRdesc_rows_list)


    return y

def apply_doubleslash_separator(x): return doubleslash_separator(x['PartNumber'], x['PR'])

def slash_separator(x, y=0):
        par_PR = []
        finalPR_list = []
        single_PRs = []
        itertools_list = []
        PR_split_del = []
        if '/' in y: 
            PR_split = y.split("+")
            for i in PR_split:
                if '/' in i:                            
                    par_PR = i.split("/")
                    itertools_list.append(par_PR)
                    #print(i)
                    #print(PR_split.index(i))
                    PR_split_del.append(i)
                    #del PR_split[PR_split.index(i)]
                    #print(par_PR)
                    #print(my_list)

            PR_split_help = PR_split
            PR_split = [x for x in PR_split_help if x not in PR_split_del]
            

            if PR_split != []:
                single_PRs.append('+'.join(PR_split))
                itertools_list.append(single_PRs)
                PR_list = list(itertools.product(*itertools_list))
                for i in PR_list:
                    finalPR_list.append('+'.join(i)) 
                    #print(finalPR_list)
            elif len(itertools_list) > 1:
                PR_list = list(itertools.product(*itertools_list))
                for i in PR_list:
                    finalPR_list.append('+'.join(i)) 
                    #print(finalPR_list)
            else:
                finalPR_list = par_PR    

            y = finalPR_list[0]
            del finalPR_list[0]
                
            for i in finalPR_list:
                dict_add = {'PartNumber': x, 'PR': i}
                rows_list.append(dict_add) 
                
             

        return y

def apply_slash_separator(x): return slash_separator(x['PartNumber'], x['PR'])


def excel_formatting(excel_file): 

    df_added = pd.DataFrame(columns=['PartNumber', 'PR'])
    

    #Read excel to data frames
    df_excel = pd.read_excel(excel_file,sheet_name=0, header=None, usecols=[0,1])   #Read excel sheet to pandas data frame
    df_excel.columns = ['PartNumber', 'PR']
    print(df_excel)

    df_excel['PartNumber'] = df_excel['PartNumber'].astype(str)

    df_excel['PartNumber'] = df_excel['PartNumber'].str.replace('_', '') #format the Part number column

    df_excel.loc[df_excel['PR'].str.startswith('+', na=False), 'PR'] = df_excel['PR'].str[1:] #Removes the '+' symbol if the PR description starts with it 

    df_excel['PR'] = df_excel.apply(apply_doubleslash_separator, axis=1)

    

    if PRdesc_rows_list != []:
        print('RRdescrowlist: ', PRdesc_rows_list)
        df_added = pd.DataFrame(PRdesc_rows_list)
        df_excel = pd.concat([df_excel, df_added])
        df_added = df_added.iloc[0:0]
        

    

    
    df_excel['PR'] = df_excel.apply(apply_slash_separator, axis=1)
    df_added = pd.DataFrame(rows_list)
    df_excel = pd.concat([df_excel, df_added])

    df_excel['PR'] = df_excel['PR'].map(sort_PR) #sort all PR numbers alphabetically in  drawing df  
    df_excel = df_excel.sort_values('PartNumber')

    return df_excel



app=Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/final_report", methods=['POST'])
def final_report():
    global rows_list
    global PRdesc_rows_list
    
    if request.method=="POST":

        if request.files['Drawing'].filename != '':
            file=request.files['Drawing']
            rows_list = []
            PRdesc_rows_list = []
            df_drawing = excel_formatting(file)
            df_drawing.to_csv(r'/Users/odusseus/Desktop/PR compare/2.0/Drawing.csv')
            drawing_out = df_drawing.to_html()
        else:
            #drawing_out = 'No Drawing file selected'
            flash('No Drawing file selected')
            return redirect(url_for('index'))

        if request.files['BOM'].filename != '':
            file=request.files['BOM']
            rows_list = []
            PRdesc_rows_list = []
            df_BOM = excel_formatting(file)
            df_BOM.to_csv(r'/Users/odusseus/Desktop/PR compare/2.0/BOM.csv')
            BOM_out = df_BOM.to_html()
        else:
            flash('No BOM file selected')
            return redirect(url_for('index'))

        df_comp = df_BOM.merge(df_drawing, indicator=True, how='outer')

        if  'left_only' in df_comp['_merge'].values:
            df_just_BOM = df_comp[df_comp._merge == 'left_only']
            del df_just_BOM['_merge']
            df_just_BOM_out = df_just_BOM.to_html(classes='table table-light table-striped', index=False, justify='left')
        else:
            df_just_BOM_out = 'There is no part number which is just in BOM'

#### Do the same like above
        df_just_Drawing = df_comp[df_comp._merge == 'right_only']
        del df_just_Drawing['_merge']

        #df.to_csv('Drawing')

    return render_template("output.html", text1=df_just_Drawing.to_html(classes='table table-light table-striped', index=False, justify='left'), text2 = df_just_BOM_out)

@app.route("/download_file/")
def download():
    return send_file()



if __name__=="__main__":
    app.run(debug=True)
