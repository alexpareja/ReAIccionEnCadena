from django.db import models

class Puntuaciones(models.Model):
    jugador = models.CharField(max_length=100);
    puntos = models.IntegerField(default=0);

    def __str__(self):
            return self.jugador

class PalabrasEncadenadas(models.Model):
    tema = models.CharField(max_length=100);
    p1 = models.CharField(max_length=20);
    p2 = models.CharField(max_length=20);
    p3 = models.CharField(max_length=20);
    p4 = models.CharField(max_length=20);
    p5 = models.CharField(max_length=20);    
    p6 = models.CharField(max_length=20);

    def __str__(self):
            return self.tema
    
class EslabonCentral(models.Model):
    p1 = models.CharField(max_length=20);
    p2 = models.CharField(max_length=20);
    p3 = models.CharField(max_length=20);
    p4 = models.CharField(max_length=20);
    p5 = models.CharField(max_length=20);    
    p6 = models.CharField(max_length=20);
    p7 = models.CharField(max_length=20);

    def __str__(self):
            return self.p1
    
class RondaFinal(models.Model):
    p1 = models.CharField(max_length=20);
    p2 = models.CharField(max_length=20);
    p3 = models.CharField(max_length=20);
    p4 = models.CharField(max_length=20);
    p5 = models.CharField(max_length=20);    
    p6 = models.CharField(max_length=20);
    p7 = models.CharField(max_length=20);
    p8 = models.CharField(max_length=20);
    p9 = models.CharField(max_length=20);
    p10 = models.CharField(max_length=20);
    p11 = models.CharField(max_length=20);
    p12 = models.CharField(max_length=20);    
    p13 = models.CharField(max_length=20);
    final = models.CharField(max_length=20);
    pista = models.CharField(max_length=20);

    def __str__(self):
            return self.p1