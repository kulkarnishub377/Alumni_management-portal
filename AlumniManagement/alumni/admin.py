from django.contrib import admin
from .models import BatchMentor, Comment, Batch

@admin.register(BatchMentor)
class BatchMentorAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'get_assigned_batches')
    
    def get_assigned_batches(self, obj):
        return ", ".join([str(batch.graduation_year) for batch in obj.assigned_batches.all()])
    get_assigned_batches.short_description = 'Assigned Batches'

    search_fields = ('username', 'email')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'created_at')
    search_fields = ('text',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('graduation_year',)
    search_fields = ('graduation_year',)
