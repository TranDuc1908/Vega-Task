import asyncio
import json
import os
from time import sleep

from playwright.async_api import async_playwright
from CustomData.loginInfo import loginEmail, loginPassword

def cleanString(rawStr):
    if not rawStr: return ""
    clnStr = str(rawStr)
    clnStr = clnStr.replace("<!---->", "")
    clnStr = clnStr.strip()
    return clnStr

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport= {"width": 1920, "height": 1080}, color_scheme="dark")
        await page.goto("https://www.linkedin.com/login")
        await page.get_by_label("Email or Phone").click()
        await page.get_by_label("Email or Phone").fill(loginEmail)
        await page.get_by_label("Password").click()
        await page.get_by_label("Password").fill(loginPassword)
        sleep(2)
        await page.get_by_role("button", name="Sign in", exact=True).click()

        
        # -------------------------------------------------------- LIST USER -------------------------------------------------------- #
        listUser = ["buidoanchung","phuongtran23","bichnhihr"]
        # -------------------------------------------------------- LIST USER -------------------------------------------------------- #



        for user in listUser:
            await page.goto(f"https://www.linkedin.com/in/{user}/")
            print("waiting")
            sleep(5)
            print("continue")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # await page.wait_for_selector(".scaffold-finite-scroll__content")

            linkedinUser = {}
            tmp_dict = {
                "full_name":"h1.text-heading-xlarge.inline.t-24.v-align-middle.break-words",
                "current_job_title":"div.text-body-medium.break-words",
                "talk_about":"div.text-body-small.t-black--light.break-words.mt2",
                "current_location":"span.text-body-small.inline.t-black--light.break-words",
                "current_company":"section.pv-top-card--website.text-body-small",
                "followers":"ul.pv-top-card--list.pv-top-card--list-bullet>li:first-child"
            }

            for k in tmp_dict:
                try:
                    item = await page.query_selector(tmp_dict[k])
                    item = await item.inner_text()
                    item = str(item).strip()
                    if k == "followers":
                        item = item.split(" ")
                        item = item[0]
                    linkedinUser[k] = item
                except: pass

            listSection = await page.query_selector_all("section.artdeco-card.ember-view.relative.break-words.pb3.mt2")
            linkedinUser["section"] = {}
            for section in listSection:
                sectionHeader = await section.query_selector("div.pvs-header__container span:first-child")
                sectionHeader = await sectionHeader.inner_text()
                sectionHeader = str(sectionHeader).strip()


                # Featured
                linkedinUser["section"][sectionHeader] = []
                if sectionHeader == "Featured":
                    listLi = await section.query_selector_all("ul.artdeco-carousel__slider.ember-view>li div.display-flex.flex-column.full-width.full-height")
                    for wrapper in listLi:
                        postType = await wrapper.query_selector("a.optional-action-target-wrapper>div>div>span")
                        if not postType: continue

                        postType = await postType.inner_text()
                        postType = cleanString(postType)

                        postURL = await wrapper.query_selector("a.optional-action-target-wrapper")
                        postURL = await postURL.get_attribute("href")
                        postURL = cleanString(postURL)

                        linkedinUser["section"][sectionHeader].append({"postType":postType, "postURL":postURL})
                
                # Activity
                elif sectionHeader == "Activity":
                    # full detail
                    loadMore = await section.query_selector("div.pvs-list__footer-wrapper a:first-child")
                    if loadMore:
                        loadMore = await loadMore.get_attribute("href")
                        loadMore = cleanString(loadMore)
                        linkedinUser["section"][sectionHeader].append({"sectionDetail":loadMore})


                    listBtn = await section.query_selector_all(":scope div.mb3>div.pv2.ph5>div>button")
                    if listBtn:
                        for btn in listBtn:
                            typeBtn = await btn.inner_text()
                            typeBtn = typeBtn.strip()
                            listLi = await section.query_selector_all(":scope div.scaffold-finite-scroll__content>ul>li")
                            if not listLi: listLi = await section.query_selector_all(":scope div.pvs-list__outer-container>ul>li")
                            if typeBtn == "Posts" or typeBtn == "Comments":
                                await btn.click()
                                for li_tag in listLi:
                                    tmp = await li_tag.query_selector(":scope div>div")

                                    highLightURL = await tmp.query_selector("a")
                                    highLightURL = await highLightURL.get_attribute("href")
                                    highLightURL = cleanString(highLightURL)

                                    content = await tmp.query_selector("a>div.inline-show-more-text>span:first-child")
                                    content = await content.inner_text()
                                    content = cleanString(content)

                                    linkedinUser["section"][sectionHeader].append({"type":typeBtn,"high_light_url":highLightURL,"content":content})
                    else:
                        listLi = await section.query_selector_all(":scope div.scaffold-finite-scroll__content>ul>li")
                        if not listLi: listLi = await section.query_selector_all(":scope div.pvs-list__outer-container>ul>li")
                        for li_tag in listLi:
                            tmp = await li_tag.query_selector(":scope div>div")

                            highLightURL = await tmp.query_selector("a")
                            highLightURL = await highLightURL.get_attribute("href")
                            highLightURL = cleanString(highLightURL)

                            content = await tmp.query_selector("a>div.inline-show-more-text>span:first-child")
                            content = await content.inner_text()
                            content = cleanString(content)

                            linkedinUser["section"][sectionHeader].append({"high_light_url":highLightURL,"content":content})
                
                # About
                elif sectionHeader == "About":
                    # full detail
                    loadMore = await section.query_selector("div.pvs-list__footer-wrapper a:first-child")
                    if loadMore:
                        loadMore = await loadMore.get_attribute("href")

                        loadMore = cleanString(loadMore)
                        linkedinUser["section"][sectionHeader].append({"sectionDetail":loadMore})


                    content = await section.query_selector("div.display-flex.ph5.pv3")
                    content = await content.query_selector("span")
                    content = await content.inner_text()
                    content = cleanString(content)
                    linkedinUser["section"][sectionHeader].append(content)
                       
                # Experience
                elif sectionHeader == "Experience":
                    # full detail
                    loadMore = await section.query_selector("div.pvs-list__footer-wrapper a:first-child")
                    if loadMore:
                        loadMore = await loadMore.get_attribute("href")
                        loadMore = cleanString(loadMore)
                        linkedinUser["section"][sectionHeader].append({"sectionDetail":loadMore})


                    listWrapper = await section.query_selector_all(":scope>div.pvs-list__outer-container>ul>li>div>div:nth-child(2)>div:first-child")
                    for wrapper in listWrapper:
                        tmp = await wrapper.query_selector(":scope>a")
                        if tmp:
                                company = await tmp.query_selector("span.mr1.hoverable-link-text.t-bold>span:first-child")
                                company = await company.inner_text()
                                company = cleanString(company)

                                totalTime = await tmp.query_selector("span.t-14.t-normal>span")
                                totalTime = await totalTime.inner_html()
                                tmp_totalTime = (totalTime.strip()).split("·")
                                for v in tmp_totalTime:
                                    if "mos" in v: totalTime = cleanString(v)

                                linkedinUser["section"][sectionHeader].append({"company":company, "total_time": totalTime})
                        else:
                                jobTitle = await wrapper.query_selector(":scope div>div>span>span:first-child")
                                jobTitle = await jobTitle.inner_text()
                                jobTitle = cleanString(jobTitle)

                                company = await wrapper.query_selector(":scope span:nth-child(2)>span:first-child")
                                company = await company.inner_text()
                                company = (company.strip()).split("·")
                                company = cleanString(company[0])

                                time = await wrapper.query_selector(":scope div>span:nth-child(3)>span:first-child")
                                time = await time.inner_text()
                                time = (time.strip()).split("·")
                                for v in time:
                                    if "mos" in v: totalTime = cleanString(v)
                                    elif "-" in v: period = cleanString(v)

                                linkedinUser["section"][sectionHeader].append({"company":company, "total_time": totalTime, "job_title": jobTitle, "period": period})
                # Education
                elif sectionHeader == "Education":
                    # full detail
                    loadMore = await section.query_selector("div.pvs-list__footer-wrapper a:first-child")
                    if loadMore:
                        loadMore = await loadMore.get_attribute("href")
                        loadMore = cleanString(loadMore)
                        linkedinUser["section"][sectionHeader].append({"sectionDetail":loadMore})


                    listItem = await section.query_selector_all(":scope div>ul>li>div>div:nth-child(2)>div:first-child>a")
                    for item in listItem:
                        tmp_dict = {
                            "school":":scope>div>span>span:first-child",
                            "speciality":":scope>span:nth-child(2)>span:first-child",
                            "period":":scope>span:nth-child(3)>span:first-child"
                        }
                        tmp_data = {}
                        for k in tmp_dict:
                            try:
                                tmp = await item.query_selector(tmp_dict[k])
                                tmp = await tmp.inner_text()
                                tmp = cleanString(tmp)
                                tmp_data[k] = tmp
                            except: print("Education fail: ->"+k)
                        linkedinUser["section"][sectionHeader].append(tmp_data)

                # Skills
                elif sectionHeader == "Skills":
                    # full detail
                    loadMore = await section.query_selector("div.pvs-list__footer-wrapper a:first-child")
                    if loadMore:
                        loadMore = await loadMore.get_attribute("href")
                        loadMore = cleanString(loadMore)
                        linkedinUser["section"][sectionHeader].append({"sectionDetail":loadMore})


                    listItem = await section.query_selector_all(":scope div>ul.pvs-list>li>div.pvs-entity--padded>div:nth-child(2)>div>a>div>span>span:first-child>a")
                    if not listItem: listItem = await section.query_selector_all(":scope div>ul.pvs-list>li>div.pvs-entity--padded>div:nth-child(2)>div>a>div>span>span:first-child")
                    for item in listItem:
                        skill = await item.inner_text()
                        skill = cleanString(skill)
                        linkedinUser["section"][sectionHeader].append(skill)                    

            if not os.path.exists("linkedinProfiles"):
                os.makedirs("linkedinProfiles")
            with open("linkedinProfiles/linkedinUser-"+cleanString(user)+".json", "w+") as f:
                linkedinUser = {k: v for k, v in linkedinUser.items() if v}
                data = json.dumps(linkedinUser)
                f.write(data)
                f.close()
            
            sleep(3)
        print("done")
        while True:
            await asyncio.sleep(1) 

asyncio.get_event_loop().run_until_complete(main())


