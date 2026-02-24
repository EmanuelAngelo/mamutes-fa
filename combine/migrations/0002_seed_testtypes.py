from django.db import migrations

def seed_test_types(apps, schema_editor):
    TestType = apps.get_model("combine", "TestType")

    data = [
        {
            "code": "40Y",
            "name": "Tiro de 40 jardas",
            "unit": "s",
            "lower_is_better": True,
        },
        {
            "code": "VJ",
            "name": "Salto Vertical",
            "unit": "cm",
            "lower_is_better": False,
        },
        {
            "code": "BJ",
            "name": "Salto à Distância",
            "unit": "m",
            "lower_is_better": False,
        },
        {
            "code": "3CONE",
            "name": "3 Cone Drill",
            "unit": "s",
            "lower_is_better": True,
        },
        {
            "code": "SHUTTLE20",
            "name": "20 yd Shuttle",
            "unit": "s",
            "lower_is_better": True,
        },
    ]

    for item in data:
        TestType.objects.update_or_create(code=item["code"], defaults=item)

def unseed_test_types(apps, schema_editor):
    TestType = apps.get_model("combine", "TestType")
    TestType.objects.filter(code__in=["40Y", "VJ", "BJ", "3CONE", "SHUTTLE20"]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ("combine", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_test_types, unseed_test_types),
    ]