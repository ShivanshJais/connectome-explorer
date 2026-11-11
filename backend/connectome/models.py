from django.db import models

class Neuron(models.Model):
    root_id = models.BigIntegerField(primary_key=True)

    # From classification.csv.gz
    flow = models.TextField(blank=True, default="")
    super_class = models.TextField(blank=True, default="")
    cell_class = models.TextField(blank=True, default="") # refers to class header in the csv file. renamed to avoid keyword conflict
    sub_class = models.TextField(blank=True, default="")
    hemilineage = models.TextField(blank=True, default="")
    side = models.TextField(blank=True, default="")
    nerve = models.TextField(blank=True, default="")

    # From neurons.csv.gz
    group = models.TextField(blank=True, default="")
    nt_type = models.TextField(blank=True, default="")

    nt_type_score = models.FloatField(null=True, blank=True)
    da_avg = models.FloatField(null=True, blank=True)
    ser_avg = models.FloatField(null=True, blank=True)
    gaba_avg = models.FloatField(null=True, blank=True)
    glut_avg = models.FloatField(null=True, blank=True)
    ach_avg = models.FloatField(null=True, blank=True)
    oct_avg = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.root_id)

class CellType(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name

class NeuronCellType(models.Model):
    id = models.BigAutoField(primary_key=True)

    neuron = models.ForeignKey(
        Neuron,
        on_delete=models.PROTECT,
        related_name="type_assignment",
    )
    cell_type = models.ForeignKey(
        CellType,
        on_delete=models.PROTECT,
        related_name="neuron_assignment"
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["neuron", "cell_type"],
                name="unique_neuron_cell_type"
            ),
            models.UniqueConstraint(
                fields=["neuron"],
                condition=models.Q(is_primary=True),
                name="one_primary_type_per_neuron"
            ),
        ]

    def __str__(self):
        return f"{self.neuron_id} -> {self.cell_type}"

class Connection(models.Model):
    id = models.BigAutoField(primary_key=True)

    pre = models.ForeignKey(
        Neuron,
        on_delete=models.PROTECT,
        related_name="outgoing_connections"
    )
    post = models.ForeignKey(
        Neuron,
        on_delete=models.PROTECT,
        related_name="incoming_connections"
    )
    neuropil = models.TextField()
    syn_count = models.PositiveIntegerField()
    nt_type = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["pre", "post", "neuropil"],
                name="unique_connection_per_neuropil",
            ),
            models.CheckConstraint(
                condition=models.Q(syn_count__gt=0),
                name="connection_syn_count_positive",
            )
        ]

    def __str__(self):
        return f"{self.pre_id} -> {self.post_id} ({self.neuropil})"