user1234 = { 
    'uid' : '1234',
    'name' : 'Darrell Huff',
    'email' : 'dh@email.com',
    'posts' : [],
}

user1235 = {
    'uid' : '1235',
    'name' : 'Irving Geis',
    'email' : 'ig@email.com',
    'posts' : [],
}

post4321 = {
    'postid' : '4321',
    'title' : '98.4% of Most Metics...',
    'body' : "Don't be a novelist --- be a statistician. Much more scope for the imagination.",
    'author' : user1234,
}

post4322 = {
    'postid' : '4322',
    'title' : '6 or a Half Dozen',
    'body' : 'Proper treatment will cure a cold in seven days, but left to itself, a cold will hang on for a week.',
    'author' : user1234,
}

user1234['posts'].append(post4321)
user1234['posts'].append(post4322)

fakedb = {
    'users' : {
        '1234' : user1234,
        '1235' : user1235,
    },

    'posts' : {
        '4321' : post4321,
        '4322' : post4322,
    }
}

__all__ = [
    'fakedb'
]
