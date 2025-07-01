from django.core.management.base import BaseCommand
from django.conf import settings
from disturbance.components.approvals.models import ApiarySiteOnApproval
from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models.functions import Distance as D

class Command(BaseCommand):
    help = 'Produce a report listing all Apiary Sites within the restricted radius ({}m) of each other.'.format(settings.RESTRICTED_RADIUS)

    def handle(self, *args, **options):
        count = 0
        site_query = ApiarySiteOnApproval.objects.filter(approval__status='current').order_by('apiary_site__id')
        bad_sites = []
        for i in site_query:
            if i.wkb_geometry:
                qs = site_query.exclude(id=i.id).filter(
                    wkb_geometry__distance_lte=(i.wkb_geometry, Distance(m=settings.RESTRICTED_RADIUS))
                ).order_by('id').annotate(
                    distance=D('wkb_geometry', i.wkb_geometry)
                )
                if qs.exists():
                    if i.apiary_site.id in list(qs.values_list('apiary_site__id',flat=True)):
                        if qs.filter(wkb_geometry__distance__gt=(i.wkb_geometry, Distance(m=0))):
                            bad_sites.append(i.apiary_site.id)
                    count += 1
                    print(i.apiary_site.id,'-',qs.values_list('apiary_site__id',flat=True),qs.values_list('distance',flat=True))
        print("{}/{} within {}m of each other".format(count,site_query.count(),settings.RESTRICTED_RADIUS))
        print("BAD SITES:", bad_sites)