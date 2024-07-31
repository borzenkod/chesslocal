from ctypes import ArgumentError
import json
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from asgiref.sync import sync_to_async

class VRel(models.Model):
    #def __init__(self, *args, **kwargs):
    #    raise ArgumentError()

    source = models.ForeignKey("Variant", related_name="source_set", on_delete=models.CASCADE)
    target = models.ForeignKey("Variant", related_name="target_set", on_delete=models.CASCADE)

# Create your models here.
class Variant(models.Model):
    fen = models.TextField()
    txt = models.TextField()
    orientation = models.TextField()
    comment = models.TextField()
    main_line = models.OneToOneField(
        'self', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='main_line_variant')
    variants = models.ManyToManyField('self', blank=True, through="VRel", symmetrical=False)
    #parent_variant = models.ForeignKey(
    #    'self', 
    #    on_delete=models.CASCADE, 
    #    null=True, 
    #    blank=True, 
    #    related_name='child_variants')

    async def get_json(self):
        return {
            "fen": self.fen, 
            "txt": self.txt, 
            "orientation": self.orientation, 
            "main": (await self.main_line.get_json()) if await sync_to_async(lambda: self.main_line is not None)() else None, 
            "variants": [await v.get_json() async for v in self.variants.all()],
            "comment": self.comment
        }

    def sync_get(self, index):
        if len(index) == 0 or isinstance(index, int):
            return self
        if index[0] == 0:
            return self.main_line.sync_get(index[1:])
        else:
            return self.variants.all()[index[0]-1].sync_get(index[1:])
    
    async def get(self, index):
        return await sync_to_async(self.sync_get)(index)    
    
    @staticmethod
    def revert_orientation(orientation):
        if orientation == 'white':
            return 'black'
        if orientation == 'black':
            return 'white'
        raise ArgumentError("Orientation is invalid")

    def sync_add(self, fen,txt,orientation,comment):
        if Variant.revert_orientation(self.orientation) != orientation:
            self.fen = fen
            self.txt = txt
            self.comment = comment
            self.save()
            return
        # Check if we have save fen main/variant
        if self.main_line is not None:
            if self.main_line.fen == fen:
                return
        # Check where to save
        variant = Variant()
        variant.fen = fen
        variant.txt = txt
        variant.orientation = orientation
        variant.comment = comment
        variant.parent_variant = self
        variant.save()
        if self.main_line is None:
            # Create new main variants
            self.main_line = variant
            self.save()
            return 0
        else: # Create new variant append to variants
            if self != variant.main_line:  # Check if it's not the main line itself
                self.variants.add(variant)
            self.save()
            return len(self.variants.all())

    async def add(self, *args):
        return await sync_to_async(self.sync_add)(*args)

@receiver(pre_delete, sender=Variant)
def delete_related_sub_variants(sender, instance, **kwargs):
    for v in instance.variants.all():
        v.delete()
    if instance.main_line:
        instance.main_line.delete()
        

class Board(models.Model):
    board_name = models.CharField(max_length=16)
    title = models.TextField(default="")

    async def get_json(self):
        return [
            await v.get_json() async for v in self.variants.all()
        ]

    def daac():
        return []
    arrows_and_circles = models.JSONField(null=False, default=daac)
    variants = models.ManyToManyField(Variant, blank=True)

    async def getH(self, index):
        print(index)
        if len(index) == 0:
            raise ArgumentError("Index lenght is 0")
        else:
            return await (
                await sync_to_async(
                    lambda: self.variants.all()[index[0]]
                )()
            ).get(index[1:])
    
    def dciv():
        return [0]
    current_index = models.JSONField(
        default=dciv
    )
    
    async def add_aac(self, color, start, end=None):
        if color in ["green", "red", "blue"]:
            obj = {
                "color": color,
                "start": start,
            }
            if end is not None:
                obj["end"] = end
            self.arrows_and_circles.append(obj)
            await self.asave()

    async def remove_aac(self, start, end=None):
        aac = self.arrows_and_circles
        filtered_aac = []
        for aoc in aac:
            if end is None:
                if start == aoc["start"] and ("end" not in aoc):
                    continue
            else:
                if start == aoc["start"] and ("end" in aoc and aoc["end"] == end):
                    continue
            filtered_aac.append(aoc)
        self.arrows_and_circles  = filtered_aac
        await self.asave()

    async def init(self):
        v = Variant()
        v.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        v.txt = "start"
        v.orientation = "white"
        v.current_index = [0]
        await v.asave()
        await self.asave()
        await self.variants.aadd(v)

    async def add_variant(self, fen,txt,orientation,comment):
        v = await self.getH(self.current_index)
        if (res :=(await v.add(fen,txt,orientation,comment))) is not None:
            self.current_index.append(res)
        await self.asave()

    def pop(self):
        tmp = self.current_index[-1]
        self.current_index = self.current_index[:-1]
        return tmp
    
    def push(self, idx):
        self.current_index.append(idx)

class Room(models.Model):
    room_uid = models.CharField(max_length=16)
    title = models.TextField(default="")

    boards = models.ManyToManyField(Board)

    current_board = models.IntegerField(default=0)

@receiver(pre_delete, sender=Board)
def delete_related_variants(sender, instance, **kwargs):
    for v in instance.variants.all():
        v.delete()
