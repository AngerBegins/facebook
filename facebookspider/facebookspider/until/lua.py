login_lua = """
            function main(splash, args)
                local ok, reason = splash:go(args.url)
                user_name = args.user_name
                user_passwd = args.user_passwd
                user_text = splash:select("#email")
                pass_text = splash:select("#pass")
                login_btn = splash:select("#loginbutton")
                if (user_text and pass_text and login_btn) then
                    user_text:send_text(user_name)
                    pass_text:send_text(user_passwd)
                    login_btn:mouse_click({})
                end

                splash:wait(math.random(5, 10))
                return {
                    url = splash:url(),
                    cookies = splash:get_cookies(),
                    headers = splash.args.headers,
                  }
            end
            """

friend_lua = """
function main(splash, args)
    local ok, reason = splash:go(args.url)
    splash:wait(math.random(5, 10))
    friend_btn = splash:select("a[data-tab-key= 'friends']") --查找最上面那栏中是否有好友这个链接
    if (friend_btn) then
        friend_btn:mouse_click({}) --点击进入好友页面
        splash:wait(math.random(5, 10))
    else
        return {
            hasFriend = false,
            cookie = splash:get_cookies(),
        }
    end

    return {
        hasFriend = true,
        html = splash:html(),
        cookie = splash:get_cookies(),
        url = splash:url(),
    }
end
"""