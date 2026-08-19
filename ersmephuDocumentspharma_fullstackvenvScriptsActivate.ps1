[1mdiff --git a/store/admin.py b/store/admin.py[m
[1mindex 2e447ca..112ece4 100644[m
[1m--- a/store/admin.py[m
[1m+++ b/store/admin.py[m
[36m@@ -39,14 +39,17 @@[m [mclass ProductVariantInline(admin.TabularInline):[m
 [m
     extra = 1[m
 [m
[31m-    fields = ([m
[32m+[m[32m    exclude = ([m
         "option_name",[m
[32m+[m[32m    )[m
[32m+[m
[32m+[m[32m    fields = ([m
         "option_value",[m
         "quantity",[m
     )[m
 [m
     verbose_name = "Variante"[m
[31m-    verbose_name_plural = "Variantes / Pointures / Tailles"[m
[32m+[m[32m    verbose_name_plural = "Tailles / Pointures / Variantes"[m
 [m
 [m
 # =========================================================[m
[36m@@ -60,6 +63,7 @@[m [mclass ProductAdmin(admin.ModelAdmin):[m
         "name",[m
         "category",[m
         "price",[m
[32m+[m[32m        "variant_type",[m
         "quantity",[m
         "total_stock",[m
         "has_variants",[m
[36m@@ -68,6 +72,7 @@[m [mclass ProductAdmin(admin.ModelAdmin):[m
 [m
     list_filter = ([m
         "category",[m
[32m+[m[32m        "variant_type",[m
         "created_at",[m
     )[m
 [m
[36m@@ -76,6 +81,17 @@[m [mclass ProductAdmin(admin.ModelAdmin):[m
         "description",[m
     )[m
 [m
[32m+[m[32m    fields = ([m
[32m+[m[32m        "category",[m
[32m+[m[32m        "name",[m
[32m+[m[32m        "description",[m
[32m+[m[32m        "price",[m
[32m+[m[32m        "variant_type",[m
[32m+[m[32m        "quantity",[m
[32m+[m[32m        "delivery",[m
[32m+[m[32m        "image",[m
[32m+[m[32m    )[m
[32m+[m
     inlines = [[m
         ProductVariantInline,[m
         ProductImageInline,[m
