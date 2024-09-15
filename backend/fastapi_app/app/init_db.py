from .database import Base, ENGINE
from .models import User, Post, Comments, Likes, Followers, Tags, PostTags, Messages


def migrate():
    Base.metadata.create_all(bind=ENGINE)