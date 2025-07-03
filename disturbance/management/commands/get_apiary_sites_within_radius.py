from django.core.management.base import BaseCommand
from django.conf import settings
from disturbance.components.approvals.models import ApiarySiteOnApproval
from disturbance.components.proposals.models import ApiarySiteOnProposal, ApiarySite
from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models.functions import Distance as D
from django.contrib.gis.db.models.functions import Transform
import datetime
import uuid
import csv
import os

class Command(BaseCommand):
    help = 'Produce a report listing all Apiary Sites within the restricted radius ({}m) of each other.'.format(settings.RESTRICTED_RADIUS)

    def handle(self, *args, **options):
        count = 0
        site_query = ApiarySiteOnApproval.objects.filter(approval__status='current').order_by('apiary_site__id')
        for i in site_query:
            if i.wkb_geometry:
                qs = site_query.exclude(id=i.id).filter(
                    wkb_geometry__distance_lte=(i.wkb_geometry, Distance(m=settings.RESTRICTED_RADIUS))
                ).order_by('id').annotate(
                    distance=D('wkb_geometry', i.wkb_geometry)
                )
                if qs.exists():
                    if i.apiary_site.id in list(qs.values_list('apiary_site__id',flat=True)):
                        qs = qs.exclude(apiary_site__id=i.apiary_site.id)
                    if qs.exists():
                        count += 1
                        #print(i.apiary_site.id,'-',qs.values_list('apiary_site__id',flat=True),qs.values_list('distance',flat=True))

        asoa_site_query = site_query
        asoa_count = count

        count = 0
        site_query = ApiarySiteOnProposal.objects.exclude(proposal_apiary__proposal__processing_status__in=['temp', 'declined', 'discarded']).order_by('apiary_site__id')
        for i in site_query:
            if i.wkb_geometry_processed:
                qs = site_query.exclude(id=i.id).filter(
                    wkb_geometry_processed__distance_lte=(i.wkb_geometry_processed, Distance(m=settings.RESTRICTED_RADIUS))
                ).order_by('id').annotate(
                    distance=D('wkb_geometry_processed', i.wkb_geometry_processed)
                )
                if qs.exists():
                    if i.apiary_site.id in list(qs.values_list('apiary_site__id',flat=True)):
                        qs = qs.exclude(apiary_site__id=i.apiary_site.id)
                    if qs.exists():
                        count += 1
                        #print(i.apiary_site.id,'-',qs.values_list('apiary_site__id',flat=True),qs.values_list('distance',flat=True))

        asop_site_query = site_query
        asop_count = count
        epsg = 4326

        site_query = ApiarySite.objects.order_by('id').annotate(
            a_geo=Transform('latest_approval_link__wkb_geometry',epsg)
        ).annotate(
            p_geo=Transform('latest_proposal_link__wkb_geometry_processed',epsg)
        )
        count = 0
        check_approval = []
        check_proposal = []
        details_dict = {}
        for i in site_query:
            if i.latest_approval_link and i.latest_proposal_link:
                if i.latest_approval_link.created_at >= i.latest_proposal_link.created_at:
                    check_approval.append(i.id)
                    details_dict[i.id] = {
                        "name":"site: {}".format(i.id), 
                        "status": i.latest_approval_link.site_status, 
                        "geo": i.a_geo,
                        "coords": i.latest_approval_link.wkb_geometry.coords,
                        "licence": i.latest_approval_link.approval.lodgement_number,
                    }
                else:
                    check_proposal.append(i.id)
                    details_dict[i.id] = {
                        "name":"site: {}".format(i.id), 
                        "status": i.latest_proposal_link.site_status, 
                        "geo": i.p_geo,
                        "coords": i.latest_proposal_link.wkb_geometry_processed.coords,
                        "proposal": i.latest_proposal_link.proposal_apiary.proposal.lodgement_number,
                    }

        for i in site_query:
            site_ids = []
            if i.id in check_approval and i.latest_approval_link and i.latest_approval_link.wkb_geometry:
                approval_qs = ApiarySiteOnApproval.objects.exclude(apiary_site__id=i.id).distinct('apiary_site__id').order_by('-id').annotate(
                        geo=Transform('wkb_geometry',epsg)
                    ).filter(
                        geo__distance_lte=(i.a_geo, Distance(m=settings.RESTRICTED_RADIUS))
                    ).order_by('apiary_site__id').annotate(
                        distance=D('geo', i.a_geo)
                    )
                #proposal_site_distances = approval_qs.values("apiary_site__id","distance")
                proposal_site_ids = list(approval_qs.values_list('apiary_site__id', flat=True))
                site_ids += list(set(check_proposal).intersection(set(proposal_site_ids)))

                proposal_approval_qs = ApiarySiteOnProposal.objects.exclude(apiary_site__id=i.id).distinct('apiary_site__id').order_by('-id').annotate(
                        geo=Transform('wkb_geometry_processed',epsg)
                    ).filter(
                        geo__distance_lte=(i.a_geo, Distance(m=settings.RESTRICTED_RADIUS))
                    ).order_by('apiary_site__id').annotate(
                        distance=D('geo', i.a_geo)
                    )
                #approval_site_distances = proposal_approval_qs.values("apiary_site__id","distance")
                approval_site_ids = list(proposal_approval_qs.values_list('apiary_site__id', flat=True))
                site_ids += list(set(check_approval).intersection(set(approval_site_ids)))
                
            if i.id in check_proposal and i.latest_proposal_link and i.latest_proposal_link.wkb_geometry_processed:
                proposal_qs = ApiarySiteOnProposal.objects.exclude(apiary_site__id=i.id).distinct('apiary_site__id').order_by('-id').annotate(
                        geo=Transform('wkb_geometry_processed',epsg)
                    ).filter(
                        geo__distance_lte=(i.p_geo, Distance(m=settings.RESTRICTED_RADIUS))
                    ).order_by('apiary_site__id').annotate(
                        distance=D('geo', i.p_geo)
                    )
                #proposal_site_distances = proposal_qs.values("apiary_site__id","distance")
                proposal_site_ids = list(proposal_qs.values_list('apiary_site__id', flat=True))
                site_ids += list(set(check_proposal).intersection(set(proposal_site_ids)))
                
                approval_proposal_qs = ApiarySiteOnApproval.objects.exclude(apiary_site__id=i.id).distinct('apiary_site__id').order_by('-id').annotate(
                        geo=Transform('wkb_geometry',epsg)
                    ).filter(
                        geo__distance_lte=(i.p_geo, Distance(m=settings.RESTRICTED_RADIUS))
                    ).order_by('apiary_site__id').annotate(
                        distance=D('geo', i.p_geo)
                    )
                #approval_site_distances = approval_proposal_qs.values("apiary_site__id","distance")
                approval_site_ids = list(approval_proposal_qs.values_list('apiary_site__id', flat=True))
                site_ids += list(set(check_approval).intersection(set(approval_site_ids)))

            site_ids = list(site_ids)
            sites_ids_coords = list(map(lambda site: {
                site:details_dict[site]["coords"]
            }, site_ids))

            if len(site_ids) > 0:
                count += 1
                print(details_dict[i.id],sites_ids_coords)
                details_dict[i.id]["site_within_restricted_radius"] = site_ids

        print("\n\nApiary Sites on Current Approvals: {}/{} within {}m of each other".format(asoa_count,asoa_site_query.count(),settings.RESTRICTED_RADIUS))
        print("Apiary Sites on Current Proposals: {}/{} within {}m of each other".format(asop_count,asop_site_query.count(),settings.RESTRICTED_RADIUS))
        print("\nAll Apiary Sites: {}/{} within {}m of each other".format(count,site_query.count(),settings.RESTRICTED_RADIUS))

        if not os.path.exists(settings.BASE_DIR+'/tmp/'):
            os.makedirs(settings.BASE_DIR+'/tmp/')

        csv_file = str(settings.BASE_DIR)+'/tmp/{}_{}_{}.csv'.format("Apiary_Sites_Report",uuid.uuid4(),int(datetime.datetime.now().timestamp()*100000))
        with open(csv_file, 'w', newline='') as new_file:
            writer = csv.writer(new_file)
            writer.writerow(["Site Number","Status","Coords", "Approval/Proposal", "Sites within Restricted Radius"])
            for i in details_dict:
                if "licence" in details_dict[i]:
                    details_dict[i]["record"] = details_dict[i]["licence"]
                elif "proposal" in details_dict[i]:
                    details_dict[i]["record"] = details_dict[i]["proposal"]
                else:
                    details_dict[i]["record"] = ""

                if "site_within_restricted_radius" in details_dict[i]:
                    details_dict[i]["sites"] = details_dict[i]["site_within_restricted_radius"]
                    writer.writerow([details_dict[i]["name"],details_dict[i]["status"],details_dict[i]["coords"],details_dict[i]["record"],details_dict[i]["sites"]])
        