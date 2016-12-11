def user_star_counter(user, starred_class):
    try:
        stars = [object.favorite_count for object in starred_class.objects.filter(owner=user)]
    except:
        stars = None
    return sum(stars)
