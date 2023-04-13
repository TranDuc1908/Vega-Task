import asyncio
import json
import pytz
import pyperclip
import os
timezone = pytz.timezone('Asia/Ho_Chi_Minh')

from datetime import datetime, timedelta
from time import sleep

from playwright.async_api import async_playwright
from CustomData.loginInfo import loginEmail, loginPassword

def cleanString(rawStr):
    if not rawStr: return ""
    clnStr = str(rawStr)
    clnStr = clnStr.replace("<!---->", "")
    clnStr = clnStr.strip()
    return clnStr

def timeAgoToDate(rawStr):
    if not rawStr: return ""
    now = datetime.now(timezone)
    rawStr = str(rawStr).replace("•","").replace("Edited","")
    rawStr = rawStr.strip()
    try: 
        if "m" in rawStr:
            timeAgo = rawStr.replace("m","")
            timeAgo = now - timedelta(minutes=int(timeAgo))
        elif "h" in rawStr:
            timeAgo = rawStr.replace("h","")
            timeAgo = now - timedelta(hours=int(timeAgo))
        elif "d" in rawStr:
            timeAgo = rawStr.replace("h","")
            timeAgo = now - timedelta(hours=24)
        else: timeAgo = "Invalid form"

        publish_date = timeAgo.strftime("%Y-%m-%d %H:%M:%S")
        return publish_date    
    except:
        print("\n")
        print(type(rawStr))
        print("Function fail: "+str(rawStr))
        print("\n")
        


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport= {"width": 1920, "height": 1080}, color_scheme="dark")
        page.set_extra_http_headers({"server":"115.76.191.23:2741"})
        await page.goto("https://www.linkedin.com/login")
        await page.get_by_label("Email or Phone").click()
        await page.get_by_label("Email or Phone").fill(loginEmail)
        await page.get_by_label("Password").click()
        await page.get_by_label("Password").fill(loginPassword)
        sleep(1)
        await page.get_by_role("button", name="Sign in", exact=True).click()
        sleep(5)
        


        # -------------------------------------------------------- LIST USER -------------------------------------------------------- #
        listKeywords = ["vietinbank","techcombank"]
        # -------------------------------------------------------- LIST USER -------------------------------------------------------- #




        for keyword in listKeywords:
            await page.goto(f"https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords={keyword}&origin=FACETED_SEARCH&sid=3Gk&sortBy=%22date_posted%22")
            print("waiting")
            sleep(5)
            print("continue")

            keepScroll = True
            while keepScroll == True:
                try:
                    await page.click("text=Show more results")
                    print("---> Loading")
                    sleep(3)

                except: 
                    print("---> Load finished")
                    keepScroll = False       
                    sleep(1)   

            print("\n")
            print("Start with keyword: "+keyword)
            listData = []
            listItem = await page.query_selector_all("ul.reusable-search__entity-result-list.list-style-none>li>div.artdeco-card>div>div")
            if listItem:
                for item in listItem:
                    data = {}
                    # author
                    authorSection = await item.query_selector(":scope>div.update-components-actor")
                    
                    authorProfile = await authorSection.query_selector(":scope>a")
                    authorProfile = await authorProfile.get_attribute("href")
                    authorProfile = cleanString(authorProfile)
                    data["author_profile"] = authorProfile

                    generalInfo = await authorSection.query_selector(":scope>a>div.update-components-actor__meta")

                    authorName = await generalInfo.query_selector(":scope>span>span>span>span")
                    authorName = await authorName.inner_text()
                    authorName = cleanString(authorName)
                    data["author"] = authorName

                    publishDate = await generalInfo.query_selector(":scope>span.update-components-actor__sub-description>div>span>span")
                    publishDate = await publishDate.inner_text()
                    publishDate = timeAgoToDate(publishDate)
                    data["publish_date"] = publishDate

                    # post detail
                    actionBtn = await item.query_selector(":scope>div.feed-shared-control-menu>div.artdeco-dropdown.artdeco-dropdown--placement-bottom.artdeco-dropdown--justification-right")
                    await actionBtn.click()
                    sleep(1)
                    h5_tags = await actionBtn.query_selector_all(":scope h5.feed-shared-control-menu__headline")
                    for tag in h5_tags:
                        tagText = await tag.inner_text()
                        if cleanString(tagText) == "Copy link to post":
                            await tag.click()
                            sleep(1)
                            href = pyperclip.paste()
                            href = cleanString(href)
                            data["post_url"] = href
                            sleep(1)

                    try:
                        content = await item.query_selector("div.update-components-text.feed-shared-update-v2__commentary")
                        content = await content.inner_text()
                        content = cleanString(content)
                        data["content"] = content
                    except: pass

                    try:
                        linkEmbed = await item.query_selector("article>div>div>a")
                        linkEmbed = await content.get_attribute("href")
                        linkEmbed = cleanString(linkEmbed)
                        data["link_embed"] = linkEmbed
                    except: pass

                    # interact
                    interactElement = await item.query_selector_all("ul.social-details-social-counts>li")
                    if interactElement:
                        for elmt in interactElement:
                            elmtText = await elmt.query_selector(":scope>button>span")
                            elmtText = await elmtText.inner_text()
                            elmtText = cleanString(elmtText)
                            if "comments" in elmtText or "comment" in elmtText:
                                elmtText = elmtText.replace("comments", "").replace("comment", "")
                                commentCount = cleanString(elmtText)
                                data["comment"] = commentCount
                            elif "reposts" in elmtText or "repost" in elmtText:
                                elmtText = elmtText.replace("reposts", "").replace("repost", "")
                                repostCount = cleanString(elmtText)
                                data["repost"] = repostCount
                            else: 
                                reactCount = cleanString(elmtText)
                                data["react"] = reactCount
                    listData.append(data)
                
                if not os.path.exists("linkedinSearch"):
                    os.makedirs("linkedinSearch")
                with open("linkedinSearch/linkedinKeyword-"+cleanString(keyword)+".json", "w+") as f:
                    data = json.dumps(listData)
                    f.write(data)
                    f.close()
            
            sleep(3)
        print("done")
        while True:
            await asyncio.sleep(1) 

asyncio.get_event_loop().run_until_complete(main())


