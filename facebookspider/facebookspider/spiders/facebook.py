# -*- coding: utf-8 -*-
import random
import re
from urllib.parse import urlparse

import scrapy
from scrapy import Selector
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy_splash import SplashFormRequest, SplashRequest

from facebookspider.items import FacebookProfile
from facebookspider.until.lua import login_lua


class FacebookSpider(scrapy.Spider):
    name = 'facebook'
    allowed_domains = ['www.facebook.com']
    # start_urls = ['http://www.facebook.com/']
    login_url = "https://www.facebook.com/login"
    def start_requests(self):
        return [
            Request(self.login_url,
                    callback=self.login)
        ]
    def login(self, response):
        facebook_email = self.settings.get('FACEBOOK_EMAIL')
        password = self.settings.get('FACEBOOK_PASS')
        if not facebook_email or not password:
            print("账号或密码不能为空")
        return SplashFormRequest.from_response(
            response,
            url= self.login_url,
            endpoint="execute",
            args={
                "wait": 30,
                "lua_source": login_lua,
                "user_name": facebook_email,
                "user_passwd": password,
            },
            formdata={
                'email': self.settings.get('FACEBOOK_EMAIL'),
                'pass': self.settings.get('FACEBOOK_PASS')
            },
            callback=self.after_login,
            errback=self.error_parse,
        )

    def after_login(self, response):
        url = response.url
        facebook_urls = self.settings.get('START_FACEBOOK_URL')
        if response.status == 200 and url in facebook_urls:
            loader = ItemLoader(item=FacebookProfile())
            #个人主页url
            profile_url = response.xpath('//a[@title="个人主页"]/@href').extract_first()
            loader.add_value('profile_url', profile_url)
            yield Request(profile_url,callback=self.parse_homepage, meta={"loader":loader})
        else:
            print("登录失败")

    def error_parse(self, response):
        print("登录失败")

    def parse_homepage(self, response):
        loader =response.meta['loader']
        loader.add_value('name',response.xpath('//span[@id="fb-timeline-cover-name"]/a/text()').extract_first())
        profile_id = re.search('profile_id=(\d+)', response.text).group(1)
        loader.add_value('profile_id',profile_id)
        yield SplashRequest(
            url=response.xpath('//a[@data-tab-key="about"]/@href').extract()[0],
            callable = self.page_about,
            meta={"loader":loader},
            encoding="execute",
            args={
                "wait": 30,
                "lua_source":
            }

        )
        friend_num = response.xpath('//a[@data-tab-key="friends"]/span[1]/text()').extract_first()
        friend_url = response.xpath('//a[@data-tab-key="friends"]/@href').extract_first()
        loader.add_value('friend', {'url':friend_url, 'num':friend_num})
        yield SplashRequest(url=friend_url,
                            callable=self._get_friends_page,
                            meta={"loader":loader},
                            endpoint="execute",
                            args={
                                "wait": 30,
                                "lua_source": login_lua,
                            }
                            )

    def _get_friends_page(self, response):
        hasFriend = response.data["hasFriend"]
        if not hasFriend:
            print("用户[%s]未开放好友查询权限" % response.meta["name"])
            return
        html = response.data["html"]
        sel = Selector(response=html)
        friends = sel.xpath("//a[@name='全部好友']")
        if friends == []:
            print("用户[%s]未开放好友查询权限" % response.meta["name"])
            return
        yield SplashRequest(
            url=response.data["url"],
            callback=self.parse_friends,
            endpoint="execute",
            cookies=random.choice(self.cookie),
            meta={"level": response.meta["level"], "name": response.meta["name"]},
            args={
                "wait": 30,
                "lua_source": lua_script,
            }
        )

        def parse_friends(self, response):
            sel = Selector(response=response)
            friends = sel.xpath("//li[@class='_698']//div[@class='fsl fwb fcb']//a")

            # 拼接lua脚本

            for friend in friends:
                url = friend.xpath(".//@href").extract_first()
                name = friend.xpath(".//text()").extract_first()

                # 记录当前好友关系
                friend_item = FBUserItem()
                friend_item["user_name"] = response.meta["name"]
                friend_item["friend_name"] = name

                print("提取到好友信息%s : %s" % (friend_item["user_name"], friend_item["friend_name"]))
                yield friend_item

                # 这里再次提交请求主要是为了获取好友的好友，以及获取好友发的帖子
                # 其实也可以在这个请求执行完成之后解析用户主页面得到用户的ID等信息
                yield SplashRequest(
                    url=url,
                    endpoint="execute",
                    callback=self.parse_main_page,
                    meta={"name": name, "level": level},
                    cookies=random.choice(self.cookie),  # 从cookie池中随机取出一个cookie
                    args={
                        "wait": 30,
                        "lua_source": lua_script,
                    }
                )

    def page_about(self,response):
        pass