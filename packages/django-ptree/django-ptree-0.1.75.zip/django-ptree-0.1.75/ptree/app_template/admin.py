from django.contrib import admin
import {{ app_name }}.models as models
import ptree.common

class ParticipantAdmin(ptree.common.ParticipantAdmin):
    readonly_fields = ptree.common.get_participant_readonly_fields([])
    list_display = ptree.common.get_participant_list_display(models.Participant,
                                                            readonly_fields=readonly_fields)

class MatchAdmin(ptree.common.MatchAdmin):
    readonly_fields = ptree.common.get_match_readonly_fields([])

    list_display = ptree.common.get_match_list_display(models.Match,
                                                       readonly_fields=readonly_fields)

class TreatmentAdmin(ptree.common.TreatmentAdmin):
    readonly_fields = ptree.common.get_treatment_readonly_fields([])
    list_display = ptree.common.get_treatment_list_display(models.Treatment,
                                                          readonly_fields=readonly_fields)

class ExperimentAdmin(ptree.common.ExperimentAdmin):
    readonly_fields = ptree.common.get_experiment_readonly_fields([])
    list_display = ptree.common.get_experiment_list_display(models.Experiment,
                                                          readonly_fields=readonly_fields)

admin.site.register(models.Participant, ParticipantAdmin)
admin.site.register(models.Match, MatchAdmin)
admin.site.register(models.Treatment, TreatmentAdmin)
admin.site.register(models.Experiment, ExperimentAdmin)

