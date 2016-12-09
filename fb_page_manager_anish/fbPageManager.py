import collections
import facebook
import requests

class FacebookPageManager:

    def __init__( self ):
        '''
            page_id : {
                name  :
                token :
                category :
            }
        '''
        self.pages_cache = collections.defaultdict()
        self.page_id =''
        self.page_token =''

    def initCache( self, pages_data):

        pages = pages_data['data']

        for page in pages:
            self.pages_cache[page['id']] = {
                'token'     : page['access_token'],
                'name'      : page['name'],
                'category'  : page['category']
            }

    def get_all_pages_info(self):
        return self.pages_cache

    def get_page_info_by_id(self,id):
        return self.pages_cache.get(id,None)

    def get_posts_per_page(self, id, token):
        '''
            * create publushed and unpublished cache on the fly
            * initialized for every page`
        '''

        self.page_id = id
        self.page_token = token

        published_posts_cache   = collections.defaultdict()
        unpublished_posts_cache = collections.defaultdict()

        graph = facebook.GraphAPI(token)
        profile = graph.get_object(id)
        posts = graph.get_connections(id, 'posts')
        post_map = {}
        for post in posts['data']:

            postid = post['id']
            # get name
            name = ''
            if 'message' in post:name = post['message']
            elif 'story' in post:name = post['story']

            # get picture , likes , comments
            endpoint = 'https://graph.facebook.com/v2.5/'+postid+ '?fields=reactions,picture,comments,is_published&access_token='+token
            response = requests.get(endpoint)
            fb_data = response.json()

            pic          = fb_data.get('picture','http://www.freeiconspng.com/uploads/no-image-icon-13.png')
            likes        = 32
            comments     = 22
            # is_published = fb_data.get('is_published',True)

            published_posts_cache[postid] = {
                'name'    : name,
                'picture' : pic,
                'likes'   : likes,
                'comments': comments
            }

        # get unpublished_posts
        endpoint_u = 'https://graph.facebook.com/v2.8/'+self.page_id+'/promotable_posts?fields=scheduled_publish_time,is_published&access_token='+token

        print(endpoint_u)
        response_u = requests.get(endpoint_u)
        fb_data_u  = response.json()

        data = fb_data_u.get('data',None)
        if data:
            for u_posts in data:
                unpublished_posts_cache[postid] = {
                        'name'        : u_posts.get('name',''),
                        'schedule'    : u_posts.get('scheduled_publish_time',None),
                        'created_time': u_posts.get('created_time','')
                    }

        return [published_posts_cache,unpublished_posts_cache]



    def get_post_details( self, postid , token):

        endpoint = 'https://graph.facebook.com/v2.5/'+postid+ '?fields=reactions,picture,comments,is_published,description,link&access_token='+token
        response = requests.get(endpoint)
        fb_data = response.json()

        pic = fb_data.get('picture','http://www.freeiconspng.com/uploads/no-image-icon-13.png')
        is_published = fb_data.get('is_published',None)

        likes = 0
        if fb_data.get('likes',None):
            likes = len(fb_data.get('likes')['data'])

        cmap ={}
        if fb_data.get('comments',None):
            comments = fb_data.get('comments')['data']
            for comment in comments:
                cmap[comment["from"]["name"]] = comment['message']


        description = fb_data.get('description',None)
        link        = fb_data.get('link',None)

        return {

          'pic':pic,
          'is_published':is_published,
          'likes':likes,
          'comments':cmap,
          'description':description,
          'link':link,
          'postid':postid

        }

    def publish_post(self, desc ):

            import facebook
            post = str(desc)
            graph = facebook.GraphAPI(self.page_token)
            graph.put_object(self.page_id, "feed", message=post)







            # import facebook
            # import requests
            # pagination
            # ACCESS_TOKEN = "my_token"
            # graph = facebook.GraphAPI(ACCESS_TOKEN)
            # friends = graph.get_connections("me","friends")
            #
            # allfriends = []
            #
            # # Wrap this block in a while loop so we can keep paginating requests until
            # # finished.
            # while(True):
            #     try:
            #         for friend in friends['data']:
            #             allfriends.append(friend['name'].encode('utf-8'))
            #         # Attempt to make a request to the next page of data, if it exists.
            #         friends=requests.get(friends['paging']['next']).json()
            #     except KeyError:
            #         # When there are no more pages (['paging']['next']), break from the
            #         # loop and end the script.
            #         break
            # print allfriends
