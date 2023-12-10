from django.db import models


# Create your models here.
class Department(models.Model):
    title = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.title} ({self.code})"

    @property
    def staff_count(self):
        if not self.pk:
            return 0
        return self.staffs.count()  # type: ignore

    @property
    def course_count(self):
        if not self.pk:
            return 0
        return self.course_set.count()  # type: ignore


class VenueCategory(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    @property
    def venues(self):
        return Venue.objects.filter(category=self.pk)

    @property
    def venue_count(self):
        if not self.pk:
            return 0
        return self.venues.count()

    class Meta:
        verbose_name_plural = "Venue Categories"


class Venue(models.Model):
    title = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField()
    category = models.ForeignKey(
        VenueCategory,
        null=True,
        related_name="venues",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"`{self.title} ({self.code})"


class Course(models.Model):
    title = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True)
    level = models.IntegerField(
        default=100,
        choices=(
            (100, "100L"),
            (200, "200L"),
            (300, "300L"),
            (400, "400L"),
            (500, "500L"),
        ),
    )
    semester = models.IntegerField(default=1, choices=((1, "First"), (2, "Second")))
    student_count = models.IntegerField()
    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="courses",
    )
    departments = models.ManyToManyField(
        Department,
    )

    def __str__(self):
        return f"{self.title} ({self.code})"


class Staff(models.Model):
    name = models.CharField(max_length=50)
    staff_id = models.CharField(
        max_length=10,
        unique=True,
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="staffs"
    )
    can_supervise = models.BooleanField(default=False)
    can_invigilate = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.department.code})"

    class Meta:
        verbose_name_plural = "Staff"
