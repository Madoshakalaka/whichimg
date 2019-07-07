# whichimg
![travis-badge](https://travis-ci.org/Madoshakalaka/whichimg.svg?branch=master)

blazing fast template matching when possible images are all known. Handy tool for GUI scripting.


## How to Use


`pip install whichimg`


```python
from whichimg import ImageTeller

teller = ImageTeller([img1, img2, img3, img4]) # numpy arrays

teller.tell(secret_img) # returns 0 or 1 or 2 or 3 or -1 for not found

```

if you're sure `secret_img` is one of the images, you can set keyword argument `surprises` to `False`. This will give you a minor performance gain.
```python
teller = ImageTeller([img1, img2, img3, img4], surprises=False)
```

This is equivalent to the following naive approach

```python
def naive_tell(images, sample_img):
    for i, img in enumerate(images):
        if np.array_equal(img, sample_img):
            return i
    return -1

naive_tell([img1, img2, img3, img4])
```



## Note

It's **not** generally faster than the naive approach. I thought my approach was faster and spent a week writing this shit though. lmfao.

They're about equally fast on the `tests/fixtures` testing data I came up with (10x10 images). Through my rought testing, there could be a magnitude of performance gain when there are many possible images (>10) and when the images are larger (200x200 for example).