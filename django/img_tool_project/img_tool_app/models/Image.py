import numpy as np

import cv2

from djongo import models

from img_tool_app.models import User


class Image(models.Model):
    id = models.IntegerField(default=1)
    owner = models.CharField(max_length=24)
    name = models.CharField(max_length=24, unique=True, primary_key=True)
    img = models.ImageField(upload_to="media")
    is_initialized = models.BooleanField(default=False)
    rule_list = models.ListField()
    defaultAction = models.CharField(default='ALLOW', max_length=10)

    def __str__(self):
        return "owner: " + self.owner + " name: " + self.name

    @classmethod
    def getImageList(cls):  # returns list of tuples
        results = []
        image_list = Image.objects.all()
        for image in image_list:
            results.append((image["owner"], image["name"]))
        return results

    def setDefault(self, action):
        self.defaultAction = action
        img = Image.objects.get(name=self.name)
        img.defaultAction = action
        img.save()

    def load(self, name):
        res = Image.objects.get(name=name)
        self.owner = res.owner

        self.name = res.name
        self.img = res.img
        self.rule_list = res.rule_list
        self.img_initialized = res.is_initialized
        self.defaultAction = res.defaultAction

    def saveDB(self, name):
        maxId = 1
        if len(Image.objects.all().order_by("-id")):
            maxId = Image.objects.all().order_by("-id")[0].id + 1
        Image.objects.create(id=maxId, owner=self.owner, name=name, rule_list=self.rule_list,
                             img=self.img,
                             defaultAction=self.defaultAction,
                             is_initialized=self.is_initialized
                             )

    @classmethod
    def delRule(self, pos):
        pos = int(pos)
        if len(self.rule_list) <= pos:
            print("Rule Not Found")
        else:
            del self.rule_list[pos]
            img = Image.objects.get(name=self.name)
            del img.rule_list[pos]
            self.rule_list = img.rule_list
            img.save()

    def addRule(self, matchexpr, shape, action, pos=-1):
        rule = {}
        if (matchexpr[0] == "u"):
            rule["type"] = "user"
        elif (matchexpr[0] == "g"):
            rule["type"] = "group"
        else:
            rule["type"] = "regex"
        img = Image.objects.get(name=self.name)
        rule["effects"] = matchexpr[2:]
        rule["shape"] = shape
        rule["action"] = action
        if (pos == -1):
            img.rule_list.append(rule)
        else:
            img.rule_list.insert(pos, rule)
        self.rule_list = img.rule_list
        img.save()

    def getImage(self, user):
        import os
        PROJECT_ROOT = os.getcwd()
        PROJECT_ROOT += '/img_tool_app/media'
        file_ = os.path.join(PROJECT_ROOT, str(self.img.name))
        f = cv2.imread(file_)
        kernel = np.ones((7, 7), np.float32) / 49
        temp_img = None
        # this part is the default part
        if self.defaultAction == "DENY":
            temp_img = np.copy(f)
            temp_img[:, :] = 0
        elif self.defaultAction == "BLUR":
            temp_img = cv2.filter2D(f, -1, kernel)
        else:
            temp_img = np.copy(f)  # almost blew up the code
        if self.rule_list:
            for rule in self.rule_list:
                rule_applies = False
                if rule["type"] == "user" and user == rule["effects"]:
                    rule_applies = True
                elif rule["type"] == "group" and User.ismember(user, rule["effects"]):
                    rule_applies = True
                elif rule["type"] == "regex":
                    regex = rule[
                        "effects"]  # TODO as far as i gather if regexsearch has this user in its results we use it
                    if User.regexsearch(user, regex):
                        rule_applies = True

                if rule_applies:
                    if rule["shape"][0] == "RECTANGLE":
                        x1 = rule["shape"][1]
                        y1 = rule["shape"][2]
                        x2 = rule["shape"][3]
                        y2 = rule["shape"][4]  # type of shape is first element of tuple(which is str)

                        if rule["action"] == "ALLOW":
                            temp_img[y1:y2, x1:x2] = f[y1:y2, x1:x2]
                        elif rule["action"] == "DENY":
                            temp_img[y1:y2, x1:x2] = 0
                        elif rule["action"] == "BLUR":
                            cropped_part = f[y1:y2, x1:x2]
                            temp_img[y1:y2, x1:x2] = cv2.filter2D(cropped_part, -1, kernel)


                        else:
                            raise ValueError  # action cannot be anything else
                    elif rule["shape"][0] == "CIRCLE":
                        x = rule["shape"][1]
                        y = rule["shape"][2]
                        r = rule["shape"][3]

                        if rule["action"] == "ALLOW":
                            black_mask = np.zeros(f.shape, dtype="uint8")  # gives us the image we need allowed
                            cv2.circle(black_mask, (x, y), r, (255, 255, 255), -1)
                            cv2.bitwise_and(f, black_mask, black_mask)

                            white_mask = np.copy(temp_img)  # need copy? just on top of temp image?
                            cv2.circle(white_mask, (x, y), r, (0, 0, 0), -1)

                            cv2.add(white_mask, black_mask, temp_img)
                        elif rule["action"] == "DENY":
                            mask = np.ones(f.shape, dtype="uint8") * 255
                            cv2.circle(mask, (x, y), r, (0, 0, 0), -1)
                            cv2.bitwise_and(temp_img, mask, temp_img)
                        elif rule["action"] == "BLUR":  # TODO improve performance
                            white_mask = np.copy(temp_img)
                            cv2.circle(white_mask, (x, y), r, (0, 0, 0), -1)  # this gives us an image with black circle

                            black_mask = np.zeros(f.shape, dtype="uint8")
                            cv2.circle(black_mask, (x, y), r, (255, 255, 255),
                                       -1)  # this gives us a black mask with white circle

                            blur_mask = np.copy(temp_img)
                            cv2.filter2D(blur_mask, -1, kernel, blur_mask)
                            cv2.bitwise_and(blur_mask, black_mask, black_mask)

                            cv2.add(white_mask, black_mask, temp_img)
                        else:
                            raise ValueError  # action cannot be anything else

                    elif rule["shape"][0] == "POLYLINE":
                        vertices = np.asarray(rule["shape"][1])
                        if rule["action"] == "ALLOW":
                            black_mask = np.zeros(f.shape, dtype="uint8")  # gives us the image we need allowed
                            cv2.fillConvexPoly(black_mask, vertices, (255, 255, 255))
                            cv2.bitwise_and(f, black_mask, black_mask)

                            white_mask = np.copy(temp_img)
                            cv2.fillConvexPoly(white_mask, vertices, (0, 0, 0))

                            cv2.add(white_mask, black_mask, temp_img)

                        elif rule["action"] == "DENY":
                            mask = np.ones(f.shape, dtype="uint8") * 255
                            cv2.fillConvexPoly(temp_img, vertices, (0, 0, 0))
                            cv2.bitwise_and(temp_img, mask, temp_img)

                        elif rule["action"] == "BLUR":  # TODO improve performance
                            white_mask = np.copy(temp_img)
                            cv2.fillConvexPoly(white_mask, vertices,
                                               (0, 0, 0))  # this gives us an image with black circle

                            black_mask = np.zeros(f.shape, dtype="uint8")
                            cv2.fillConvexPoly(black_mask, vertices,
                                               (255, 255, 255))  # this gives us a black mask with white circle

                            blur_mask = np.copy(temp_img)
                            cv2.filter2D(blur_mask, -1, kernel, blur_mask)
                            cv2.bitwise_and(blur_mask, black_mask, black_mask)

                            cv2.add(white_mask, black_mask, temp_img)
                        else:
                            raise ValueError  # action cannot be anything else

                    else:
                        raise ValueError  # if this happens shape is given incorrectly

        return temp_img
