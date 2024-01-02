#libraries used in the script
import streamlit as st
import pandas as pd
import requests
import json 
from io import StringIO

def convert_df(df):
    return df.to_csv().encode('utf-8')

#Introduction 
st.title('Download data from archive.org')
st.markdown(
'''Archive.org application done by [Antoine Eripret](https://www.aeripret.com/). You can report a bug or an issue in [Github](https://github.com/antoineeripret/streamlit-archive).

Get saved pages for a specific domain from Wayback Machine. The application can get **up to 100.000 URLs** using archive.org's API. **This limit is applied on the request sent to archive.org: the output file can be smaller based on the condition you choose to apply below**. 

''')

#file extensions 
file_ext = ['AAC','ABW','ARC','AVIF','AVI','AZW','BIN','BMP','BZ','BZ2','CDA','CSH','CSS','CSV','DOC','DOCX','EOT','EPUB','GZ','GIF','HTM','HTML','ICO','ICS','JAR','JPEG','JPG','JS','JSON','JSONLD','MID','MIDI','MJS','MP3','MP4','MPEG','MPKG','ODP','ODS','ODT','OGA','OGV','OGX','OPUS','OTF','PNG','PDF','PHP','PPT','PPTX','RAR','RTF','SH','SVG','TAR','TIF','TIFF','TS','TTF','TXT','VSD','WAV','WEBA','WEBM','WEBP','WOFF','WOFF2','XHTML','XLS','XLSX','XML','XUL','ZIP','3GP','3G2','7Z']
#input from user 
domain = st.text_input('Domain (e.g. liligo.fr) ')
from_date = st.date_input('Date FROM (YYY-MM-DD)')
to_date = st.date_input('Date TO (YYY-MM-DD)')
extensions_to_exclude = st.multiselect('File extensions to exclude (you can pick several)', file_ext)
parameters = st.checkbox('Keep URLs with parameters as separated entries?')

if st.button('Extract data'):
    st.write('Extraction can take a moment based on the number of URLs available in the API.')

    extensions_to_exclude = ['\.'+element.lower() for element in extensions_to_exclude]
    from_date_str = from_date.strftime("%Y%m%d")
    to_date_str = from_date.strftime("%Y%m%d")
    
    params = {
  'url': domain,
  'collapse':'urlkey',
  'matchType':'prefix',
  'output': 'txt',
  'from': from_date_str,
  'to': to_date_str, 
  'limit':100000
}
    headers = {'User-Agent':'download-application-streamlit'}
    r = requests.get('http://web.archive.org/cdx/search/cdx', params=params, headers=headers)
    try: 
      csv = pd.read_csv(StringIO(r.text), sep=' ')
    except:
      st.write('No data available for this domain.')
      csv = None 
    if csv is not None: 
      csv.loc[len(csv)] = csv.columns.tolist()
      csv.columns = ['urlkey','timestamp','url','type','rc','digest','length']
      if extensions_to_exclude:
        csv = csv[csv['url'].str.contains('|'.join(extensions_to_exclude), regex=True)==False]
      csv['archive_url'] = 'http://web.archive.org/web/'+csv['timestamp'].astype(str)+'/'+csv['url']
      csv['url'] = csv['url'].str.replace(':80','')
      if parameters == False:
          csv['url'] = csv['url'].str.replace('\?.*','' ,regex=True)
      csv = csv[['url','type','archive_url']].drop_duplicates(subset='url')
      csv = convert_df(csv)
  
      st.download_button(
          "Press to download file",
          csv,
          "file.csv",
          "text/csv",
          key='download-csv'
          )
