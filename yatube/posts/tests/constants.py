from django.urls import reverse

MAIN_URL_NAME = 'posts:index'
GROUP_URL_NAME = 'posts:group_list'
PROFILE_URL_NAME = 'posts:profile'
POST_DETAIL_URL_NAME = 'posts:post_detail'
POST_CREATE_URL_NAME = 'posts:post_create'
POST_EDIT_URL_NAME = 'posts:post_edit'
LOGIN_URL_NAME = 'users:login'
ADD_COMMENT_URL_NAME = 'posts:add_comment'
FOLLOW_INDEX_URL_NAME = 'posts:follow_index'
PROFILE_FOLLOW_URL_NAME = 'posts:profile_follow'
PROFILE_UNFOLLOW_URL_NAME = 'posts:profile_unfollow'

MAIN_TEMPL = 'posts/index.html'
GROUP_TEMPL = 'posts/group_list.html'
PROFILE_TEMPL = 'posts/profile.html'
POST_DETAIL_TEMPL = 'posts/post_detail.html'
POST_CREATE_TEMPL = 'posts/create_post.html'
FOLLOW_TEMPL = 'posts/follow.html'

NONEXIST_URL = '/nonexist/'
LOGIN_NEXT_CREATE_URL = (
    reverse(LOGIN_URL_NAME) + '?next=' + reverse(POST_CREATE_URL_NAME)
)


SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
