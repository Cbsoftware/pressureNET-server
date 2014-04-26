SHARING_PUBLIC = 'Public'
SHARING_RESEARCHERS_FORECASTERS = 'Us, Researchers and Forecasters'
SHARING_RESEARCHERS = 'Us and Researchers'
SHARING_PRIVATE = 'Cumulonimbus (Us)'
#SHARING_NOBODY = 'Nobody'

SHARING_CHOICES = (
    (SHARING_PUBLIC, 'Public'),
    (SHARING_RESEARCHERS_FORECASTERS, 'Researchers and Forecasters'),
    (SHARING_RESEARCHERS, 'Researchers'),
    (SHARING_PRIVATE, 'Private'),
    # 'Nobody' data should be rejected #96
    #(SHARING_NOBODY, 'Nobody'),
)
