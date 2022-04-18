import feedparser
from flask import Flask, render_template,request
import requests 
import pandas as pd
from bs4 import BeautifulSoup as bs
from flask_paginate import Pagination, get_page_args



def get_bbc_text(url):
    """Parse bbc article and return text in list of strings"""
    
    article = requests.get(url)
    articles = bs(article.content, "html.parser")
    articles_body = articles.findAll('article')
    p_blocks = articles_body[0].findAll('p') 
    p_blocks_df=pd.DataFrame(columns=['element_name','parent_hierarchy','element_text','element_text_Count'])
    for i in range(0,len(p_blocks)):
        parents_list=[]
        for parent in p_blocks[i].parents:
            #Extract the parent id attribute if it exists
            Parent_id = ''
            try:
                Parent_id = parent['id']
            except:
                pass
            
            # Append the parent name and id to the parents table
            parents_list.append(parent.name + 'id: ' + Parent_id)
    
        # 2.2 Construct parents hierarchy
        parent_element_list = ['' if (x == 'None' or x is None) else x for x in parents_list ]
        parent_element_list.reverse()
        parent_hierarchy = ' -> '.join(parent_element_list)
    
    #Append data table with the current paragraph data
        p_blocks_df=p_blocks_df.append({"element_name":p_blocks[i].name
                                        ,"parent_hierarchy":parent_hierarchy
                                        ,"element_text":p_blocks[i].text
                                        ,"element_text_Count":len(str(p_blocks[i].text))}
                                        ,ignore_index=True
                                        ,sort=False)
        
    # 3. concatenate paragraphs under the same parent hierarchy
        if len(p_blocks_df)>0:
            p_blocks_df_groupby_parent_hierarchy=p_blocks_df.groupby(by=['parent_hierarchy'])
            p_blocks_df_groupby_parent_hierarchy_sum=p_blocks_df_groupby_parent_hierarchy[['element_text_Count']].sum()            
            p_blocks_df_groupby_parent_hierarchy_sum.reset_index(inplace=True)            

    # 4. count paragraphs length
    # 5. select the longest paragraph as the main article
    maxid=p_blocks_df_groupby_parent_hierarchy_sum.loc[p_blocks_df_groupby_parent_hierarchy_sum['element_text_Count'].idxmax()
                                                        ,'parent_hierarchy']
    merge_text='</p><p>'.join(p_blocks_df.loc[p_blocks_df['parent_hierarchy']==maxid,'element_text'].to_list())
    return merge_text
def get_bbc_title(url:str) -> str:
    """Parse bbc article and return the Title"""
    
    article = requests.get(url)
    articles = bs(article.content, "html.parser")
    articles_body = articles.findAll('article')
    title = articles_body[0].find('h1') 
    return title
def get_bbc_image(url:str) -> str:
    """Parse bbc article and return the Title"""
    
    article = requests.get(url)
    articles = bs(article.content, "html.parser")
    articles_body = articles.findAll('article')
    image = articles_body[0].findAll('img') 
    return image
app = Flask(__name__)

RSS_FEEDS = ['http://feeds.bbci.co.uk/news/rss.xml?edition=int',
             'http://rss.cnn.com/rss/edition.rss',
             'http://feeds.foxnews.com/foxnews/latest'
             ]




@app.route("/")
def index():
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page, per_page, offset = get_page_args(page_parameter='page',per_page_parameter='per_page',type=int, default=1)    
    pagination_articles = get_articles(offset=offset,per_page=per_page)
    pagination = Pagination(page=page, total=len(feed),per_page=per_page, record_name='articles')
    return render_template("index.html", articles=pagination_articles,pagination=pagination,page=page,per_page=int(per_page))
@app.route("/extract")
def extract():
    feedid = request.args.get('feedId')
    parsed = get_bbc_text(feedid)
    title = get_bbc_title(feedid)
    image=get_bbc_image(feedid)
    return render_template("handyextract.html",body=parsed,title=title,image=image)

def get_feed():
    posts = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for post in feed.entries:
            posts.append((post))
    return posts
feed =  get_feed()
def get_articles(offset=0,per_page=5):
    return feed[offset:offset+per_page]

if __name__ == "__main__":
    app.run(port=5000, debug=True)