from .base import BaseNormalizer
from .reddit import RedditNormalizer
from .facebook import FacebookNormalizer
from .threads import ThreadsNormalizer

NORMALIZERS = {
    "reddit": RedditNormalizer,
    "facebook": FacebookNormalizer,
    "threads": ThreadsNormalizer,
}
