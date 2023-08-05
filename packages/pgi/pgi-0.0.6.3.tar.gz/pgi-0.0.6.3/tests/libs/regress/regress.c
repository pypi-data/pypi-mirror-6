/* -*- mode: C; c-file-style: "gnu"; indent-tabs-mode: nil; -*- */
#include <string.h>
#include <stdlib.h>
#include <glib-object.h>
#include <gobject/gvaluecollector.h>

#include "regress.h"

static gboolean abort_on_error = TRUE;

#define ASSERT_VALUE(condition)  \
  if (abort_on_error)             \
    g_assert (condition);         \
  else                            \
    g_warn_if_fail (condition);   \

void
regress_set_abort_on_error (gboolean in)
{
  abort_on_error = in;
}

/* basic types */
gboolean
regress_test_boolean (gboolean in)
{
  return in;
}

gboolean
regress_test_boolean_true (gboolean in)
{
  ASSERT_VALUE (in == TRUE);
  return in;
}

gboolean
regress_test_boolean_false (gboolean in)
{
  ASSERT_VALUE (in == FALSE);
  return in;
}

gint8
regress_test_int8 (gint8 in)
{
  return in;
}

guint8
regress_test_uint8 (guint8 in)
{
  return in;
}

gint16
regress_test_int16 (gint16 in)
{
  return in;
}

guint16
regress_test_uint16 (guint16 in)
{
  return in;
}

gint32
regress_test_int32 (gint32 in)
{
  return in;
}

guint32
regress_test_uint32 (guint32 in)
{
  return in;
}

gint64
regress_test_int64 (gint64 in)
{
  return in;
}

guint64
regress_test_uint64 (guint64 in)
{
  return in;
}

gshort
regress_test_short (gshort in)
{
  return in;
}

gushort
regress_test_ushort (gushort in)
{
  return in;
}

gint
regress_test_int (gint in)
{
  return in;
}

guint
regress_test_uint (guint in)
{
  return in;
}

glong
regress_test_long (glong in)
{
  return in;
}

gulong
regress_test_ulong (gulong in)
{
  return in;
}

gssize
regress_test_ssize (gssize in)
{
  return in;
}

gsize
regress_test_size (gsize in)
{
  return in;
}

gfloat
regress_test_float (gfloat in)
{
  return in;
}

gdouble
regress_test_double (gdouble in)
{
  return in;
}

gunichar
regress_test_unichar (gunichar in)
{
  return in;
}

time_t
regress_test_timet (time_t in)
{
  return in;
}

GType
regress_test_gtype (GType in)
{
  return in;
}

int
regress_test_closure (GClosure *closure)
{
  GValue return_value = {0, };
  int ret;

  g_value_init (&return_value, G_TYPE_INT);

  g_closure_invoke (closure,
                    &return_value,
                    0, NULL,
                    NULL);

  ret = g_value_get_int (&return_value);

  g_value_unset(&return_value);

  return ret;
}

int
regress_test_closure_one_arg (GClosure *closure, int arg)
{
  GValue return_value = {0, };
  GValue arguments[1];
  int ret;

  g_value_init (&return_value, G_TYPE_INT);

  memset (&arguments[0], 0, sizeof (arguments));
  g_value_init (&arguments[0], G_TYPE_INT);
  g_value_set_int (&arguments[0], arg);

  g_closure_invoke (closure,
                    &return_value,
                    1, arguments,
                    NULL);

  ret = g_value_get_int (&return_value);

  g_value_unset(&return_value);
  g_value_unset(&arguments[0]);

  return ret;
}

/**
 * regress_test_closure_variant:
 * @closure: GClosure which takes one GVariant and returns a GVariant
 * @arg: (allow-none) (transfer none): a GVariant passed as argument to @closure
 *
 * Return value: (transfer full): the return value of @closure
 */
GVariant*
regress_test_closure_variant (GClosure *closure, GVariant* arg)
{
  GValue return_value = {0, };
  GValue arguments[1] = {{0,} };
  GVariant *ret;

  g_value_init (&return_value, G_TYPE_VARIANT);

  g_value_init (&arguments[0], G_TYPE_VARIANT);
  g_value_set_variant (&arguments[0], arg);

  g_closure_invoke (closure,
                    &return_value,
                    1, arguments,
                    NULL);

  ret = g_value_get_variant (&return_value);
  if (ret != NULL)
    g_variant_ref (ret);

  g_value_unset (&return_value);
  g_value_unset (&arguments[0]);

  return ret;
}

/**
 * regress_test_value_arg:
 * @v: (transfer none): a GValue expected to contain an int
 *
 * Return value: the int contained in the GValue.
 */
int
regress_test_int_value_arg(const GValue *v)
{
  int i;

  i = g_value_get_int (v);

  return i;
}

static GValue value;
/**
 * regress_test_value_return:
 * @i: an int
 *
 * Return value: (transfer none): the int wrapped in a GValue.
 */
const GValue *
regress_test_value_return(int i)
{
  memset(&value, '\0', sizeof(GValue));

  g_value_init (&value, G_TYPE_INT);
  g_value_set_int (&value, i);

  return &value;
}

/************************************************************************/
/* foreign structs */

#ifndef _GI_DISABLE_CAIRO
/**
 * regress_test_cairo_context_full_return:
 *
 * Returns: (transfer full):
 */
cairo_t *
regress_test_cairo_context_full_return (void)
{
  cairo_surface_t *surface;
  cairo_t *cr;
  surface = cairo_image_surface_create (CAIRO_FORMAT_ARGB32, 10, 10);
  cr = cairo_create (surface);
  cairo_surface_destroy (surface);
  return cr;
}

/**
 * regress_test_cairo_context_none_in:
 * @context: (transfer none):
 */
void
regress_test_cairo_context_none_in (cairo_t *context)
{
  cairo_surface_t *surface = cairo_get_target (context);

  g_assert (cairo_image_surface_get_format (surface) == CAIRO_FORMAT_ARGB32);
  g_assert (cairo_image_surface_get_width (surface) == 10);
  g_assert (cairo_image_surface_get_height (surface) == 10);
}


/**
 * regress_test_cairo_surface_none_return:
 *
 * Returns: (transfer none):
 */
cairo_surface_t *
regress_test_cairo_surface_none_return (void)
{
  static cairo_surface_t *surface;

  if (surface == NULL) {
    surface = cairo_image_surface_create (CAIRO_FORMAT_ARGB32, 10, 10);
  }

  return surface;
}

/**
 * regress_test_cairo_surface_full_return:
 *
 * Returns: (transfer full):
 */
cairo_surface_t *
regress_test_cairo_surface_full_return (void)
{
  return cairo_image_surface_create (CAIRO_FORMAT_ARGB32, 10, 10);
}

/**
 * regress_test_cairo_surface_none_in:
 * @surface: (transfer none):
 */
void
regress_test_cairo_surface_none_in (cairo_surface_t *surface)
{
  g_assert (cairo_image_surface_get_format (surface) == CAIRO_FORMAT_ARGB32);
  g_assert (cairo_image_surface_get_width (surface) == 10);
  g_assert (cairo_image_surface_get_height (surface) == 10);
}

/**
 * regress_test_cairo_surface_full_out:
 * @surface: (out) (transfer full):
 */
void
regress_test_cairo_surface_full_out (cairo_surface_t **surface)
{
  *surface = cairo_image_surface_create (CAIRO_FORMAT_ARGB32, 10, 10);
}
#endif

/**
 * regress_test_gvariant_i:
 *
 * Returns: (transfer none): New variant
 */
GVariant *
regress_test_gvariant_i (void)
{
  return g_variant_new_int32 (1);
}

/**
 * regress_test_gvariant_s:
 *
 * Returns: (transfer none): New variant
 */
GVariant *
regress_test_gvariant_s (void)
{
  return g_variant_new_string ("one");
}

/**
 * regress_test_gvariant_asv:
 *
 * Returns: (transfer none): New variant
 */
GVariant *
regress_test_gvariant_asv (void)
{
  GVariantBuilder b;

  g_variant_builder_init (&b, G_VARIANT_TYPE ("a{sv}"));

  g_variant_builder_add (&b, "{sv}", "name", g_variant_new_string ("foo"));
  g_variant_builder_add (&b, "{sv}", "timeout", g_variant_new_int32 (10));

  return g_variant_builder_end (&b);
}

/**
 * regress_test_gvariant_v:
 *
 * Returns: (transfer none): New variant
 */
GVariant *
regress_test_gvariant_v (void)
{
  return g_variant_new_variant (g_variant_new_string ("contents"));
}

/**
 * regress_test_gvariant_as:
 *
 * Returns: (transfer none): New variant
 */
GVariant *
regress_test_gvariant_as (void)
{
  const char *as[] = { "one", "two", "three", NULL };

  return g_variant_new_strv (as, -1);
}

/************************************************************************/
/* utf8 */
/* insert BLACK HEART SUIT to ensure UTF-8 doesn't get mangled */
static const char utf8_const[]    = "const \xe2\x99\xa5 utf8";
static const char utf8_nonconst[] = "nonconst \xe2\x99\xa5 utf8";

/**
 * regress_test_utf8_const_return:
 *
 * Return value: UTF-8 string
 */
const char *
regress_test_utf8_const_return (void)
{
  /* transfer mode none */
  return utf8_const;
}

/**
 * regress_test_utf8_nonconst_return:
 *
 * Return value: (transfer full): UTF-8 string
 */
char *
regress_test_utf8_nonconst_return (void)
{
  return g_strdup (utf8_nonconst);
}

/**
 * regress_test_utf8_const_in:
 *
 */
void
regress_test_utf8_const_in (const char *in)
{
  /* transfer mode none */
  g_assert (strcmp (in, utf8_const) == 0);
}

/**
 * regress_test_utf8_out:
 * @out: (out) (transfer full):
 */
void
regress_test_utf8_out (char **out)
{
  /* out parameter, transfer mode full */
  *out = g_strdup (utf8_nonconst);
}

/**
 * regress_test_utf8_inout:
 * @inout: (inout) (transfer full):
 */
void
regress_test_utf8_inout (char **inout)
{
  /* inout parameter, transfer mode full */
  g_assert (strcmp (*inout, utf8_const) == 0);
  *inout = g_strdup (utf8_nonconst);
}

/**
 * regress_test_filename_return:
 *
 * Return value: (element-type filename) (transfer full): list of strings
 */
GSList *
regress_test_filename_return (void)
{
  GSList *filenames = NULL;
  filenames = g_slist_prepend (filenames, g_filename_from_utf8("/etc/fstab", -1, NULL, NULL, NULL));
  filenames = g_slist_prepend (filenames, g_filename_from_utf8("åäö", -1, NULL, NULL, NULL));
  return filenames;
}

/* in arguments after out arguments */

/**
 * regress_test_int_out_utf8:
 * @length: (out):
 * @in:
 */
void
regress_test_int_out_utf8 (int *length, const char *in)
{
    *length = g_utf8_strlen(in, -1);
}


/* multiple output arguments */

/**
 * regress_test_multi_double_args:
 * @in:
 * @one: (out):
 * @two: (out):
 */
void
regress_test_multi_double_args (gdouble in, gdouble *one, gdouble *two)
{
  *one = in * 2;
  *two = in * 3;
}

/**
 * regress_test_utf8_out_out:
 * @out0: (out) (transfer full): a copy of "first"
 * @out1: (out) (transfer full): a copy of "second"
 */
void
regress_test_utf8_out_out (char **out0, char **out1)
{
  *out0 = g_strdup ("first");
  *out1 = g_strdup ("second");
}

/**
 * regress_test_utf8_out_nonconst_return:
 * @out: (out) (transfer full): a copy of "second"
 *
 * Returns: (transfer full): a copy of "first"
 */
char *
regress_test_utf8_out_nonconst_return (char **out)
{
  *out = g_strdup ("second");
  return g_strdup ("first");
}

/**
 * regress_test_utf8_null_in:
 * @in: (allow-none):
 */
void
regress_test_utf8_null_in (char *in)
{
  g_assert (in == NULL);
}

/**
 * regress_test_utf8_null_out:
 * @char_out: (allow-none) (out):
 */
void regress_test_utf8_null_out (char **char_out)
{
  *char_out = NULL;
}


/* non-basic-types */

static const char *test_sequence[] = {"1", "2", "3"};

/* array */

/**
 * regress_test_array_int_in:
 * @n_ints:
 * @ints: (array length=n_ints): List of ints
 */
int
regress_test_array_int_in (int n_ints, int *ints)
{
  int i, sum = 0;
  for (i = 0; i < n_ints; i++)
    sum += ints[i];
  return sum;
}

/**
 * regress_test_array_int_out:
 * @n_ints: (out): the length of @ints
 * @ints: (out) (array length=n_ints) (transfer full): a list of 5 integers, from 0 to 4 in consecutive order
 */
void
regress_test_array_int_out (int *n_ints, int **ints)
{
  int i;
  *n_ints = 5;
  *ints = g_malloc0(sizeof(**ints) * *n_ints);
  for (i = 1; i < *n_ints; i++)
    (*ints)[i] = (*ints)[i-1] + 1;
}

/**
 * regress_test_array_int_inout:
 * @n_ints: (inout): the length of @ints
 * @ints: (inout) (array length=n_ints) (transfer full): a list of integers whose items will be increased by 1, except the first that will be dropped
 */
void
regress_test_array_int_inout (int *n_ints, int **ints)
{
  int i;
  int *new_ints;

  if (0 < *n_ints)
    {
      *n_ints -= 1;
      new_ints = g_malloc(sizeof(**ints) * *n_ints);
      for (i = 0; i < *n_ints; i++)
	new_ints[i] = (*ints)[i + 1] + 1;
      *ints = new_ints;
    }
}

/**
 * regress_test_array_gint8_in:
 * @n_ints:
 * @ints: (array length=n_ints): List of ints
 */
int
regress_test_array_gint8_in (int n_ints, gint8 *ints)
{
  int i, sum = 0;
  for (i = 0; i < n_ints; i++)
    sum += ints[i];
  return sum;
}

/**
 * regress_test_array_gint16_in:
 * @n_ints:
 * @ints: (array length=n_ints): List of ints
 */
int
regress_test_array_gint16_in (int n_ints, gint16 *ints)
{
  int i, sum = 0;
  for (i = 0; i < n_ints; i++)
    sum += ints[i];
  return sum;
}

/**
 * regress_test_array_gint32_in:
 * @n_ints:
 * @ints: (array length=n_ints): List of ints
 */
gint32
regress_test_array_gint32_in (int n_ints, gint32 *ints)
{
  int i;
  gint32 sum = 0;
  for (i = 0; i < n_ints; i++)
    sum += ints[i];
  return sum;
}

/**
 * regress_test_array_gint64_in:
 * @n_ints:
 * @ints: (array length=n_ints): List of ints
 */
gint64
regress_test_array_gint64_in (int n_ints, gint64 *ints)
{
  int i;
  gint64 sum = 0;
  for (i = 0; i < n_ints; i++)
    sum += ints[i];
  return sum;
}

/**
 * regress_test_strv_in:
 * @arr: (array zero-terminated=1) (transfer none):
 */
gboolean
regress_test_strv_in (char **arr)
{
  if (g_strv_length (arr) != 3)
    return FALSE;
  if (strcmp (arr[0], "1") != 0)
    return FALSE;
  if (strcmp (arr[1], "2") != 0)
    return FALSE;
  if (strcmp (arr[2], "3") != 0)
    return FALSE;
  return TRUE;
}

/**
 * regress_test_array_gtype_in:
 * @n_types:
 * @types: (array length=n_types): List of types
 *
 * Return value: (transfer full): string representation of provided types
 */
char *
regress_test_array_gtype_in (int n_types, GType *types)
{
  GString *string;
  int i;

  string = g_string_new ("[");
  for (i = 0; i < n_types; i++)
    {
      g_string_append (string, g_type_name (types[i]));
      g_string_append_c (string, ',');
    }
  g_string_append_c (string, ']');
  return g_string_free (string, FALSE);
}

/**
 * regress_test_strv_out:
 *
 * Returns: (transfer full):
 */
char **
regress_test_strv_out (void)
{
  int i = 0;
  int n = 6;
  char **ret = g_new (char *, n);
  ret[i++] = g_strdup ("thanks");
  ret[i++] = g_strdup ("for");
  ret[i++] = g_strdup ("all");
  ret[i++] = g_strdup ("the");
  ret[i++] = g_strdup ("fish");
  ret[i++] = NULL;
  g_assert (i == n);
  return ret;
}

/**
 * regress_test_strv_out_container:
 *
 * Return value: (array zero-terminated=1) (transfer container):
 */
char **
regress_test_strv_out_container (void)
{
  char **ret = g_new (char *, 4);
  ret[0] = "1";
  ret[1] = "2";
  ret[2] = "3";
  ret[3] = NULL;
  return ret;
}

/**
 * regress_test_strv_outarg:
 * @retp: (array zero-terminated=1) (out) (transfer container):
 */
void
regress_test_strv_outarg (char ***retp)
{
  char **ret = g_new (char *, 4);
  ret[0] = "1";
  ret[1] = "2";
  ret[2] = "3";
  ret[3] = NULL;
  *retp = ret;
}

/**
 * regress_test_array_fixed_size_int_in:
 * @ints: (array fixed-size=5): a list of 5 integers
 *
 * Returns: the sum of the items in @ints
 */
int
regress_test_array_fixed_size_int_in (int *ints)
{
  int i, sum = 0;
  for (i = 0; i < 5; i++)
    sum += ints[i];
  return sum;
}

/**
 * regress_test_array_fixed_size_int_out:
 * @ints: (out) (array fixed-size=5) (transfer full): a list of 5 integers ranging from 0 to 4
 */
void
regress_test_array_fixed_size_int_out (int **ints)
{
  int i;
  *ints = g_malloc0(sizeof(**ints) * 5);
  for (i = 1; i < 5; i++)
    (*ints)[i] = (*ints)[i-1] + 1;
}

/**
 * regress_test_array_fixed_size_int_return:
 *
 * Returns: (array fixed-size=5) (transfer full): a list of 5 integers ranging from 0 to 4
 */
int *
regress_test_array_fixed_size_int_return (void)
{
  int i, *ints;
  ints = g_malloc0(sizeof(*ints) * 5);
  for (i = 1; i < 5; i++)
    ints[i] = ints[i-1] + 1;
  return ints;
}

/**
 * regress_test_strv_out_c:
 *
 * Returns: (transfer none):
 */
const char * const*
regress_test_strv_out_c (void)
{
  static char **ret = NULL;

  if (ret == NULL)
    ret = regress_test_strv_out ();

  return (const char * const *) ret;
}

/**
 * regress_test_array_int_full_out:
 * @len: length of the returned array.
 *
 * Returns: (array length=len) (transfer full): a new array of integers.
 */
int *
regress_test_array_int_full_out(int *len)
{
  int *result, i;
  *len = 5;
  result = g_malloc0(sizeof(*result) * (*len));
  for (i=1; i < (*len); i++)
    result[i] = result[i-1] + 1;
  return result;
}

/**
 * regress_test_array_int_none_out:
 * @len: length of the returned array.
 *
 * Returns: (array length=len) (transfer none): a static array of integers.
 */
int *
regress_test_array_int_none_out(int *len)
{
  static int result[5] = { 1, 2, 3, 4, 5 };
  *len = 5;
  return result;
}

/**
 * regress_test_array_int_null_in:
 * @arr: (array length=len) (allow-none):
 * @len: length
 */
void
regress_test_array_int_null_in (int *arr, int len)
{
  g_assert (arr == NULL);
}

/**
 * regress_test_array_int_null_out:
 * @arr: (out) (array length=len) (allow-none):
 * @len: (out) : length
 */
void
regress_test_array_int_null_out (int **arr, int *len)
{
  *arr = NULL;
  *len = 0;
}

/* interface */

/************************************************************************/
/* GList */

static /*const*/ GList *
regress_test_sequence_list (void)
{
    static GList *list = NULL;
    if (!list) {
        gsize i;
        for (i = 0; i < G_N_ELEMENTS(test_sequence); ++i) {
            list = g_list_prepend (list, (gpointer)test_sequence[i]);
        }
        list = g_list_reverse (list);
    }
    return list;
}

/**
 * regress_test_glist_nothing_return:
 *
 * Return value: (element-type utf8) (transfer none):
 */
const GList *
regress_test_glist_nothing_return (void)
{
  return regress_test_sequence_list ();
}

/**
 * regress_test_glist_nothing_return2:
 *
 * Return value: (element-type utf8) (transfer none):
 */
GList *
regress_test_glist_nothing_return2 (void)
{
  return regress_test_sequence_list ();
}

/**
 * regress_test_glist_container_return:
 *
 * Return value: (element-type utf8) (transfer container):
 */
GList *
regress_test_glist_container_return (void)
{
  return g_list_copy (regress_test_sequence_list ());
}

/**
 * regress_test_glist_everything_return:
 *
 * Return value: (element-type utf8) (transfer full):
 */
GList *
regress_test_glist_everything_return (void)
{
  GList *list;
  GList *l;

  list = g_list_copy (regress_test_sequence_list ());
  for (l = list; l != NULL; l = l->next)
      l->data = g_strdup (l->data);
  return list;
}

static void
regress_assert_test_sequence_list (const GList *in)
{
  const GList *l;
  gsize i;

  for (i = 0, l = in; l != NULL; ++i, l = l->next) {
      g_assert (i < G_N_ELEMENTS(test_sequence));
      g_assert (strcmp (l->data, test_sequence[i]) == 0);
  }
  g_assert (i == G_N_ELEMENTS(test_sequence));
}

/**
 * regress_test_glist_nothing_in:
 * @in: (element-type utf8):
 */
void
regress_test_glist_nothing_in (const GList *in)
{
  regress_assert_test_sequence_list (in);
}

/**
 * regress_test_glist_nothing_in2:
 * @in: (element-type utf8):
 */
void
regress_test_glist_nothing_in2 (GList *in)
{
  regress_assert_test_sequence_list (in);
}

/**
 * regress_test_glist_null_in:
 * @in: (element-type utf8) (allow-none):
 */
void
regress_test_glist_null_in (GSList *in)
{
  g_assert (in == NULL);
}

/**
 * regress_test_glist_null_out:
 * @out_list: (out) (element-type utf8) (allow-none):
 */
void
regress_test_glist_null_out (GSList **out_list)
{
  *out_list = NULL;
}


/************************************************************************/
/* GSList */

static /*const*/ GSList *
regress_test_sequence_slist (void)
{
    static GSList *list = NULL;
    if (!list) {
        gsize i;
        for (i = 0; i < G_N_ELEMENTS(test_sequence); ++i) {
            list = g_slist_prepend (list, (gpointer)test_sequence[i]);
        }
        list = g_slist_reverse (list);
    }
    return list;
}

/**
 * regress_test_gslist_nothing_return:
 *
 * Return value: (element-type utf8) (transfer none):
 */
const GSList *
regress_test_gslist_nothing_return (void)
{
  return regress_test_sequence_slist ();
}

/**
 * regress_test_gslist_nothing_return2:
 *
 * Return value: (element-type utf8) (transfer none):
 */
GSList *
regress_test_gslist_nothing_return2 (void)
{
  return regress_test_sequence_slist ();
}

/**
 * regress_test_gslist_container_return:
 *
 * Return value: (element-type utf8) (transfer container):
 */
GSList *
regress_test_gslist_container_return (void)
{
  return g_slist_copy (regress_test_sequence_slist ());
}

/**
 * regress_test_gslist_everything_return:
 *
 * Return value: (element-type utf8) (transfer full):
 */
GSList *
regress_test_gslist_everything_return (void)
{
  GSList *list;
  GSList *l;

  list = g_slist_copy (regress_test_sequence_slist ());
  for (l = list; l != NULL; l = l->next)
      l->data = g_strdup (l->data);
  return list;
}

static void
regress_assert_test_sequence_slist (const GSList *in)
{
  const GSList *l;
  gsize i;

  for (i = 0, l = in; l != NULL; ++i, l = l->next) {
      g_assert (i < G_N_ELEMENTS(test_sequence));
      g_assert (strcmp (l->data, test_sequence[i]) == 0);
  }
  g_assert (i == G_N_ELEMENTS(test_sequence));
}

/**
 * regress_test_gslist_nothing_in:
 * @in: (element-type utf8):
 */
void
regress_test_gslist_nothing_in (const GSList *in)
{
  regress_assert_test_sequence_slist (in);
}

/**
 * regress_test_gslist_nothing_in2:
 * @in: (element-type utf8):
 */
void
regress_test_gslist_nothing_in2 (GSList *in)
{
  regress_assert_test_sequence_slist (in);
}

/**
 * regress_test_gslist_null_in:
 * @in: (element-type utf8) (allow-none):
 */
void
regress_test_gslist_null_in (GSList *in)
{
  g_assert (in == NULL);
}

/**
 * regress_test_gslist_null_out:
 * @out_list: (out) (element-type utf8) (allow-none):
 */
void
regress_test_gslist_null_out (GSList **out_list)
{
  *out_list = NULL;
}

/************************************************************************/
/* GHash */

static char *table_data[3][2] = {
  { "foo", "bar" }, { "baz", "bat" }, { "qux", "quux" }
};

static GHashTable *
regress_test_table_ghash_new_container (void)
{
  GHashTable *hash;
  int i;
  hash = g_hash_table_new(g_str_hash, g_str_equal);
  for (i=0; i<3; i++)
    g_hash_table_insert(hash, table_data[i][0], table_data[i][1]);
  return hash;
}

static GHashTable *
regress_test_table_ghash_new_full (void)
{
  GHashTable *hash;
  int i;
  hash = g_hash_table_new_full(g_str_hash, g_str_equal, g_free, g_free);
  for (i=0; i<3; i++)
    g_hash_table_insert(hash,
                        g_strdup(table_data[i][0]),
                        g_strdup(table_data[i][1]));
  return hash;
}

static /*const*/ GHashTable *
regress_test_table_ghash_const (void)
{
  static GHashTable *hash = NULL;
  if (!hash) {
    hash = regress_test_table_ghash_new_container();
  }
  return hash;
}

/**
 * regress_test_ghash_null_return:
 *
 * Return value: (element-type utf8 utf8) (transfer none) (allow-none):
 */
const GHashTable *
regress_test_ghash_null_return (void)
{
  return NULL;
}

/**
 * regress_test_ghash_nothing_return:
 *
 * Return value: (element-type utf8 utf8) (transfer none):
 */
const GHashTable *
regress_test_ghash_nothing_return (void)
{
  return regress_test_table_ghash_const ();
}

/**
 * regress_test_ghash_nothing_return2:
 *
 * Return value: (element-type utf8 utf8) (transfer none):
 */
GHashTable *
regress_test_ghash_nothing_return2 (void)
{
  return regress_test_table_ghash_const ();
}

static GValue *
g_value_new (GType type)
{
  GValue *value = g_slice_new0(GValue);
  g_value_init(value, type);
  return value;
}

static void
g_value_free (GValue *value)
{
  g_value_unset(value);
  g_slice_free(GValue, value);
}

static const gchar *string_array[] = {
  "first",
  "second",
  "third",
  NULL
};

/**
 * regress_test_ghash_gvalue_return:
 *
 * Return value: (element-type utf8 GValue) (transfer none):
 */
GHashTable *
regress_test_ghash_gvalue_return (void)
{
  GHashTable *hash;
  GValue *value;
  hash = g_hash_table_new_full(g_str_hash, g_str_equal,
                               g_free, (GDestroyNotify)g_value_free);

  value = g_value_new(G_TYPE_INT);
  g_value_set_int(value, 12);
  g_hash_table_insert(hash, g_strdup("integer"), value);

  value = g_value_new(G_TYPE_BOOLEAN);
  g_value_set_boolean(value, TRUE);
  g_hash_table_insert(hash, g_strdup("boolean"), value);

  value = g_value_new(G_TYPE_STRING);
  g_value_set_string(value, "some text");
  g_hash_table_insert(hash, g_strdup("string"), value);

  value = g_value_new(G_TYPE_STRV);
  g_value_set_boxed(value, string_array);
  g_hash_table_insert(hash, g_strdup("strings"), value);

  value = g_value_new(REGRESS_TEST_TYPE_FLAGS);
  g_value_set_flags(value, REGRESS_TEST_FLAG1 | REGRESS_TEST_FLAG3);
  g_hash_table_insert(hash, g_strdup("flags"), value);

  value = g_value_new(regress_test_enum_get_type());
  g_value_set_enum(value, REGRESS_TEST_VALUE2);
  g_hash_table_insert(hash, g_strdup("enum"), value);

  return hash;
}

/**
 * regress_test_ghash_gvalue_in:
 * @hash: (element-type utf8 GValue): the hash table returned by
 * regress_test_ghash_gvalue_return().
 */
void
regress_test_ghash_gvalue_in (GHashTable *hash)
{
  GValue *value;
  const gchar **strings;
  int i;

  g_assert(hash != NULL);

  value = g_hash_table_lookup(hash, "integer");
  g_assert(value != NULL);
  g_assert(G_VALUE_HOLDS_INT(value));
  g_assert(g_value_get_int(value) == 12);

  value = g_hash_table_lookup(hash, "boolean");
  g_assert(value != NULL);
  g_assert(G_VALUE_HOLDS_BOOLEAN(value));
  g_assert(g_value_get_boolean(value) == TRUE);

  value = g_hash_table_lookup(hash, "string");
  g_assert(value != NULL);
  g_assert(G_VALUE_HOLDS_STRING(value));
  g_assert(strcmp(g_value_get_string(value), "some text") == 0);

  value = g_hash_table_lookup(hash, "strings");
  g_assert(value != NULL);
  g_assert(G_VALUE_HOLDS(value, G_TYPE_STRV));
  strings = g_value_get_boxed(value);
  g_assert(strings != NULL);
  for (i = 0; string_array[i] != NULL; i++)
    g_assert(strcmp(strings[i], string_array[i]) == 0);

  value = g_hash_table_lookup(hash, "flags");
  g_assert(value != NULL);
  g_assert(G_VALUE_HOLDS_FLAGS(value));
  g_assert(g_value_get_flags(value) == (REGRESS_TEST_FLAG1 | REGRESS_TEST_FLAG3));

  value = g_hash_table_lookup(hash, "enum");
  g_assert(value != NULL);
  g_assert(G_VALUE_HOLDS_ENUM(value));
  g_assert(g_value_get_enum(value) == REGRESS_TEST_VALUE2);
}

/**
 * regress_test_ghash_container_return:
 *
 * Return value: (element-type utf8 utf8) (transfer container):
 */
GHashTable *
regress_test_ghash_container_return (void)
{
  return regress_test_table_ghash_new_container ();
}

/**
 * regress_test_ghash_everything_return:
 *
 * Return value: (element-type utf8 utf8) (transfer full):
 */
GHashTable *
regress_test_ghash_everything_return (void)
{
  return regress_test_table_ghash_new_full ();
}

static void
assert_test_table_ghash (const GHashTable *in)
{
  GHashTable *h = regress_test_table_ghash_const();
  GHashTableIter iter;
  gpointer key, value;

  g_assert(g_hash_table_size(h) ==
           g_hash_table_size((GHashTable*)in));

  g_hash_table_iter_init(&iter, (GHashTable*)in);
  while (g_hash_table_iter_next (&iter, &key, &value))
    g_assert( strcmp(g_hash_table_lookup(h, (char*)key), (char*)value) == 0);
}

/**
 * regress_test_ghash_null_in:
 * @in: (element-type utf8 utf8) (allow-none):
 */
void
regress_test_ghash_null_in (const GHashTable *in)
{
  g_assert (in == NULL);
}

/**
 * regress_test_ghash_null_out:
 * @out: (element-type utf8 utf8) (allow-none) (out):
 */
void
regress_test_ghash_null_out (const GHashTable **out)
{
  *out = NULL;
}

/**
 * regress_test_ghash_nothing_in:
 * @in: (element-type utf8 utf8):
 */
void
regress_test_ghash_nothing_in (const GHashTable *in)
{
  assert_test_table_ghash (in);
}

/**
 * regress_test_ghash_nothing_in2:
 * @in: (element-type utf8 utf8):
 */
void
regress_test_ghash_nothing_in2 (GHashTable *in)
{
  assert_test_table_ghash (in);
}

/* Nested collection types */

/**
 * regress_test_ghash_nested_everything_return:
 *
 * Specify nested parameterized types directly with the (type ) annotation.
 *
 * Return value: (type GLib.HashTable<utf8,GLib.HashTable<utf8,utf8>>) (transfer full):
 */
GHashTable *
regress_test_ghash_nested_everything_return (void)
{
  GHashTable *hash;
  hash = g_hash_table_new_full(g_str_hash, g_str_equal, g_free,
                               (void (*) (gpointer)) g_hash_table_destroy);
  g_hash_table_insert(hash, g_strdup("wibble"), regress_test_table_ghash_new_full());
  return hash;
}

/**
 * regress_test_ghash_nested_everything_return2:
 *
 * Another way of specifying nested parameterized types: using the
 * element-type annotation.
 *
 * Return value: (element-type utf8 GLib.HashTable<utf8,utf8>) (transfer full):
 */
GHashTable *
regress_test_ghash_nested_everything_return2 (void)
{
  return regress_test_ghash_nested_everything_return();
}

/************************************************************************/

/**
 * regress_test_garray_container_return:
 *
 * Returns: (transfer container) (type GLib.PtrArray) (element-type utf8):
 */
GPtrArray *
regress_test_garray_container_return (void)
{
  GPtrArray *array;

  array = g_ptr_array_new_with_free_func (g_free);
  g_ptr_array_add (array, g_strdup ("regress"));

  return array;
}

/**
 * regress_test_garray_full_return:
 *
 * Returns: (transfer full) (type GLib.PtrArray) (element-type utf8):
 */
GPtrArray *
regress_test_garray_full_return (void)
{
  GPtrArray *array;

  array = g_ptr_array_new ();
  g_ptr_array_add (array, g_strdup ("regress"));

  return array;
}

/************************************************************************/

/* error? */

/* enums / flags */

/**
 * NUM_REGRESS_FOO: (skip)
 *
 * num of elements in RegressFoo
 */

GType
regress_test_enum_get_type (void)
{
    static GType etype = 0;
    if (G_UNLIKELY(etype == 0)) {
        static const GEnumValue values[] = {
            { REGRESS_TEST_VALUE1, "REGRESS_TEST_VALUE1", "value1" },
            { REGRESS_TEST_VALUE2, "REGRESS_TEST_VALUE2", "value2" },
            { REGRESS_TEST_VALUE3, "REGRESS_TEST_VALUE3", "value3" },
            { REGRESS_TEST_VALUE4, "REGRESS_TEST_VALUE4", "value4" },
            { 0, NULL, NULL }
        };
        etype = g_enum_register_static (g_intern_static_string ("RegressTestEnum"), values);
    }

    return etype;
}

GType
regress_test_enum_unsigned_get_type (void)
{
    static GType etype = 0;
    if (G_UNLIKELY(etype == 0)) {
        static const GEnumValue values[] = {
            { REGRESS_TEST_UNSIGNED_VALUE1, "REGRESS_TEST_UNSIGNED_VALUE1", "value1" },
            { REGRESS_TEST_UNSIGNED_VALUE2, "REGRESS_TEST_UNSIGNED_VALUE2", "value2" },
            { 0, NULL, NULL }
        };
        etype = g_enum_register_static (g_intern_static_string ("RegressTestEnumUnsigned"), values);
    }

    return etype;
}

GType
regress_test_flags_get_type (void)
{
    static GType etype = 0;
    if (G_UNLIKELY(etype == 0)) {
        static const GFlagsValue values[] = {
            { REGRESS_TEST_FLAG1, "TEST_FLAG1", "flag1" },
            { REGRESS_TEST_FLAG2, "TEST_FLAG2", "flag2" },
            { REGRESS_TEST_FLAG3, "TEST_FLAG3", "flag3" },
            { 0, NULL, NULL }
        };
        etype = g_flags_register_static (g_intern_static_string ("RegressTestFlags"), values);
    }

    return etype;
}

const gchar *
regress_test_enum_param(RegressTestEnum e)
{
  GEnumValue *ev;
  GEnumClass *ec;

  ec = g_type_class_ref (regress_test_enum_get_type ());
  ev = g_enum_get_value (ec, e);
  g_type_class_unref (ec);

  return ev->value_nick;
}

const gchar *
regress_test_unsigned_enum_param(RegressTestEnumUnsigned e)
{
  GEnumValue *ev;
  GEnumClass *ec;

  ec = g_type_class_ref (regress_test_enum_unsigned_get_type ());
  ev = g_enum_get_value (ec, e);
  g_type_class_unref (ec);

  return ev->value_nick;
}

/**
 * regress_global_get_flags_out:
 * @v: (out): A flags value
 *
 */
void
regress_global_get_flags_out (RegressTestFlags *v)
{
  *v = REGRESS_TEST_FLAG1 | REGRESS_TEST_FLAG3;
}

/* error domains */

GType
regress_test_error_get_type (void)
{
    static GType etype = 0;
    if (G_UNLIKELY(etype == 0)) {
        static const GEnumValue values[] = {
            { REGRESS_TEST_ERROR_CODE1, "REGRESS_TEST_ERROR_CODE1", "code1" },
            { REGRESS_TEST_ERROR_CODE2, "REGRESS_TEST_ERROR_CODE2", "code2" },
            { REGRESS_TEST_ERROR_CODE3, "REGRESS_TEST_ERROR_CODE3", "code3" },
            { 0, NULL, NULL }
        };
        etype = g_enum_register_static (g_intern_static_string ("RegressTestError"), values);
    }

    return etype;
}

GQuark
regress_test_error_quark (void)
{
  return g_quark_from_static_string ("regress-test-error");
}

GType
regress_test_abc_error_get_type (void)
{
    static GType etype = 0;
    if (G_UNLIKELY(etype == 0)) {
        static const GEnumValue values[] = {
            { REGRESS_TEST_ABC_ERROR_CODE1, "REGRESS_TEST_ABC_ERROR_CODE1", "code1" },
            { REGRESS_TEST_ABC_ERROR_CODE2, "REGRESS_TEST_ABC_ERROR_CODE2", "code2" },
            { REGRESS_TEST_ABC_ERROR_CODE3, "REGRESS_TEST_ABC_ERROR_CODE3", "code3" },
            { 0, NULL, NULL }
        };
        etype = g_enum_register_static (g_intern_static_string ("RegressTestABCError"), values);
    }

    return etype;
}

GQuark
regress_test_abc_error_quark (void)
{
  return g_quark_from_static_string ("regress-test-abc-error");
}

GType
regress_test_unconventional_error_get_type (void)
{
    static GType etype = 0;
    if (G_UNLIKELY(etype == 0)) {
        static const GEnumValue values[] = {
            { REGRESS_TEST_OTHER_ERROR_CODE1, "REGRESS_TEST_OTHER_ERROR_CODE1", "code1" },
            { REGRESS_TEST_OTHER_ERROR_CODE2, "REGRESS_TEST_OTHER_ERROR_CODE2", "code2" },
            { REGRESS_TEST_OTHER_ERROR_CODE3, "REGRESS_TEST_OTHER_ERROR_CODE3", "code3" },
            { 0, NULL, NULL }
        };
        etype = g_enum_register_static (g_intern_static_string ("RegressTestOtherError"), values);
    }

    return etype;
}

GQuark
regress_test_unconventional_error_quark (void)
{
  return g_quark_from_static_string ("regress-test-other-error");
}


GQuark
regress_test_def_error_quark (void)
{
  return g_quark_from_static_string ("regress-test-def-error");
}

GQuark
regress_atest_error_quark (void)
{
  return g_quark_from_static_string ("regress-atest-error");
}

/* structures */

/**
 * regress_test_struct_a_clone:
 * @a: the structure
 * @a_out: (out caller-allocates): the cloned structure
 *
 * Make a copy of a RegressTestStructA
 */
void
regress_test_struct_a_clone (RegressTestStructA *a,
		     RegressTestStructA *a_out)
{
  *a_out = *a;
}

/**
 * regress_test_struct_a_parse:
 * @a_out: (out caller-allocates): the structure that is to be filled
 * @string: ignored
 */
void
regress_test_struct_a_parse (RegressTestStructA *a_out,
                             const gchar *string)
{
	a_out->some_int = 23;
}

/**
 * regress_test_struct_b_clone:
 * @b: the structure
 * @b_out: (out): the cloned structure
 *
 * Make a copy of a RegressTestStructB
 */
void
regress_test_struct_b_clone (RegressTestStructB *b,
		     RegressTestStructB *b_out)
{
  *b_out = *b;
}

/* plain-old-data boxed types */

RegressTestSimpleBoxedA *
regress_test_simple_boxed_a_copy (RegressTestSimpleBoxedA *a)
{
  RegressTestSimpleBoxedA *new_a = g_slice_new (RegressTestSimpleBoxedA);

  *new_a = *a;

  return new_a;
}

static void
regress_test_simple_boxed_a_free (RegressTestSimpleBoxedA *a)
{
  g_slice_free (RegressTestSimpleBoxedA, a);
}

GType
regress_test_simple_boxed_a_get_gtype (void)
{
  static GType our_type = 0;

  if (our_type == 0)
    our_type = g_boxed_type_register_static (g_intern_static_string ("RegressTestSimpleBoxedA"),
					     (GBoxedCopyFunc)regress_test_simple_boxed_a_copy,
					     (GBoxedFreeFunc)regress_test_simple_boxed_a_free);
  return our_type;
}

RegressTestSimpleBoxedB *
regress_test_simple_boxed_b_copy (RegressTestSimpleBoxedB *b)
{
  RegressTestSimpleBoxedB *new_b = g_slice_new (RegressTestSimpleBoxedB);

  *new_b = *b;

  return new_b;
}

gboolean
regress_test_simple_boxed_a_equals (RegressTestSimpleBoxedA *a,
			    RegressTestSimpleBoxedA *other_a)
{
  return (a->some_int == other_a->some_int &&
	  a->some_int8 == other_a->some_int8 &&
	  a->some_double == other_a->some_double);
}

const RegressTestSimpleBoxedA*
regress_test_simple_boxed_a_const_return (void)
{
  static RegressTestSimpleBoxedA simple_a = {
    5, 6, 7.0
  };

  return &simple_a;
}

static void
regress_test_simple_boxed_b_free (RegressTestSimpleBoxedB *a)
{
  g_slice_free (RegressTestSimpleBoxedB, a);
}

GType
regress_test_simple_boxed_b_get_type (void)
{
  static GType our_type = 0;

  if (our_type == 0)
    our_type = g_boxed_type_register_static (g_intern_static_string ("RegressTestSimpleBoxedB"),
					     (GBoxedCopyFunc)regress_test_simple_boxed_b_copy,
					     (GBoxedFreeFunc)regress_test_simple_boxed_b_free);
  return our_type;
}

/* opaque boxed */

struct _RegressTestBoxedPrivate
{
  guint magic;
};

/**
 * regress_test_boxed_new:
 *
 * Returns: (transfer full):
 */
RegressTestBoxed *
regress_test_boxed_new (void)
{
  RegressTestBoxed *boxed = g_slice_new0(RegressTestBoxed);
  boxed->priv = g_slice_new0(RegressTestBoxedPrivate);
  boxed->priv->magic = 0xdeadbeef;

  return boxed;
}

/**
 * regress_test_boxed_new_alternative_constructor1:
 *
 * Returns: (transfer full):
 */
RegressTestBoxed *
regress_test_boxed_new_alternative_constructor1 (int i)
{
  RegressTestBoxed *boxed = g_slice_new0(RegressTestBoxed);
  boxed->priv = g_slice_new0(RegressTestBoxedPrivate);
  boxed->priv->magic = 0xdeadbeef;
  boxed->some_int8 = i;

  return boxed;
}

/**
 * regress_test_boxed_new_alternative_constructor2:
 *
 * Returns: (transfer full):
 */
RegressTestBoxed *
regress_test_boxed_new_alternative_constructor2 (int i, int j)
{
  RegressTestBoxed *boxed = g_slice_new0(RegressTestBoxed);
  boxed->priv = g_slice_new0(RegressTestBoxedPrivate);
  boxed->priv->magic = 0xdeadbeef;
  boxed->some_int8 = i + j;

  return boxed;
}

/**
 * regress_test_boxed_new_alternative_constructor3:
 *
 * Returns: (transfer full):
 */
RegressTestBoxed *
regress_test_boxed_new_alternative_constructor3 (char *s)
{
  RegressTestBoxed *boxed = g_slice_new0(RegressTestBoxed);
  boxed->priv = g_slice_new0(RegressTestBoxedPrivate);
  boxed->priv->magic = 0xdeadbeef;
  boxed->some_int8 = atoi(s);

  return boxed;
}

/**
 * regress_test_boxed_copy:
 *
 * Returns: (transfer full):
 */
RegressTestBoxed *
regress_test_boxed_copy (RegressTestBoxed *boxed)
{
  RegressTestBoxed *new_boxed = regress_test_boxed_new();
  RegressTestBoxedPrivate *save;

  save = new_boxed->priv;
  *new_boxed = *boxed;
  new_boxed->priv = save;

  return new_boxed;
}

gboolean
regress_test_boxed_equals (RegressTestBoxed *boxed,
		   RegressTestBoxed *other)
{
  return (other->some_int8 == boxed->some_int8 &&
	  regress_test_simple_boxed_a_equals(&other->nested_a, &boxed->nested_a));
}

static void
regress_test_boxed_free (RegressTestBoxed *boxed)
{
  g_assert (boxed->priv->magic == 0xdeadbeef);

  g_slice_free (RegressTestBoxedPrivate, boxed->priv);
  g_slice_free (RegressTestBoxed, boxed);
}

GType
regress_test_boxed_get_type (void)
{
  static GType our_type = 0;

  if (our_type == 0)
    our_type = g_boxed_type_register_static (g_intern_static_string ("RegressTestBoxed"),
					     (GBoxedCopyFunc)regress_test_boxed_copy,
					     (GBoxedFreeFunc)regress_test_boxed_free);
  return our_type;
}

RegressTestBoxedB *
regress_test_boxed_b_new (gint8 some_int8, glong some_long)
{
  RegressTestBoxedB *boxed;

  boxed = g_slice_new (RegressTestBoxedB);
  boxed->some_int8 = some_int8;
  boxed->some_long = some_long;

  return boxed;
}

RegressTestBoxedB *
regress_test_boxed_b_copy (RegressTestBoxedB *boxed)
{
  return regress_test_boxed_b_new (boxed->some_int8, boxed->some_long);
}

static void
regress_test_boxed_b_free (RegressTestBoxedB *boxed)
{
  g_slice_free (RegressTestBoxedB, boxed);
}

G_DEFINE_BOXED_TYPE(RegressTestBoxedB,
                    regress_test_boxed_b,
                    regress_test_boxed_b_copy,
                    regress_test_boxed_b_free);

RegressTestBoxedC *
regress_test_boxed_c_new (void)
{
  RegressTestBoxedC *boxed;

  boxed = g_slice_new (RegressTestBoxedC);
  boxed->refcount = 1;
  boxed->another_thing = 42; /* what else */

  return boxed;
}

static RegressTestBoxedC *
regress_test_boxed_c_ref (RegressTestBoxedC *boxed)
{
  g_atomic_int_inc (&boxed->refcount);
  return boxed;
}

static void
regress_test_boxed_c_unref (RegressTestBoxedC *boxed)
{
  if (g_atomic_int_dec_and_test (&boxed->refcount)) {
    g_slice_free (RegressTestBoxedC, boxed);
  }
}

G_DEFINE_BOXED_TYPE(RegressTestBoxedC,
                    regress_test_boxed_c,
                    regress_test_boxed_c_ref,
                    regress_test_boxed_c_unref);

struct _RegressTestBoxedD {
  char *a_string;
  gint a_int;
};

RegressTestBoxedD *
regress_test_boxed_d_new (const char *a_string, int a_int)
{
  RegressTestBoxedD *boxed;

  boxed = g_slice_new (RegressTestBoxedD);
  boxed->a_string = g_strdup (a_string);
  boxed->a_int = a_int;

  return boxed;
}

RegressTestBoxedD *
regress_test_boxed_d_copy (RegressTestBoxedD *boxed)
{
  RegressTestBoxedD *ret;

  ret = g_slice_new (RegressTestBoxedD);
  ret->a_string = g_strdup (boxed->a_string);
  ret->a_int = boxed->a_int;

  return ret;
}

void
regress_test_boxed_d_free (RegressTestBoxedD *boxed)
{
  g_free (boxed->a_string);
  g_slice_free (RegressTestBoxedD, boxed);
}

int
regress_test_boxed_d_get_magic (RegressTestBoxedD *boxed)
{
  return strlen (boxed->a_string) + boxed->a_int;
}

G_DEFINE_BOXED_TYPE(RegressTestBoxedD,
                    regress_test_boxed_d,
                    regress_test_boxed_d_copy,
                    regress_test_boxed_d_free);

G_DEFINE_TYPE(RegressTestObj, regress_test_obj, G_TYPE_OBJECT);

enum
{
  PROP_TEST_OBJ_BARE = 1,
  PROP_TEST_OBJ_BOXED,
  PROP_TEST_OBJ_HASH_TABLE,
  PROP_TEST_OBJ_LIST,
  PROP_TEST_OBJ_HASH_TABLE_OLD,
  PROP_TEST_OBJ_LIST_OLD,
  PROP_TEST_OBJ_INT,
  PROP_TEST_OBJ_FLOAT,
  PROP_TEST_OBJ_DOUBLE,
  PROP_TEST_OBJ_STRING,
  PROP_TEST_OBJ_GTYPE
};

static void
regress_test_obj_set_property (GObject      *object,
                       guint         property_id,
                       const GValue *value,
                       GParamSpec   *pspec)
{
  RegressTestObj *self = REGRESS_TEST_OBJECT (object);
  GList *list;

  switch (property_id)
    {
    case PROP_TEST_OBJ_BARE:
      regress_test_obj_set_bare (self, g_value_get_object (value));
      break;

    case PROP_TEST_OBJ_BOXED:
      if (self->boxed)
        regress_test_boxed_free (self->boxed);
      self->boxed = g_value_dup_boxed (value);
      break;

    case PROP_TEST_OBJ_HASH_TABLE:
    case PROP_TEST_OBJ_HASH_TABLE_OLD:
      if (self->hash_table)
        g_hash_table_unref (self->hash_table);
      self->hash_table = g_hash_table_ref (g_value_get_boxed (value));
      break;

    case PROP_TEST_OBJ_LIST:
    case PROP_TEST_OBJ_LIST_OLD:
      if (self->list != NULL)
        {
          for (list = self->list; list != NULL; list = g_list_next (list))
            g_free (list->data);
          g_list_free (self->list);
        }
      self->list = NULL;
      for (list = g_value_get_pointer (value); list != NULL; list = g_list_next (list))
        self->list = g_list_append (self->list, g_strdup (list->data));
      break;

    case PROP_TEST_OBJ_INT:
      self->some_int8 = g_value_get_int (value);
      break;

    case PROP_TEST_OBJ_FLOAT:
      self->some_float = g_value_get_float (value);
      break;

    case PROP_TEST_OBJ_DOUBLE:
      self->some_double = g_value_get_double (value);
      break;

    case PROP_TEST_OBJ_STRING:
      self->string = g_value_dup_string (value);
      break;

    case PROP_TEST_OBJ_GTYPE:
      self->gtype = g_value_get_gtype (value);
      break;

    default:
      /* We don't have any other property... */
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
      break;
    }
}

static void
regress_test_obj_get_property (GObject    *object,
                        guint       property_id,
                        GValue     *value,
                        GParamSpec *pspec)
{
  RegressTestObj *self = REGRESS_TEST_OBJECT (object);

  switch (property_id)
    {
    case PROP_TEST_OBJ_BARE:
      g_value_set_object (value, self->bare);
      break;

    case PROP_TEST_OBJ_BOXED:
      g_value_set_boxed (value, self->boxed);
      break;

    case PROP_TEST_OBJ_HASH_TABLE:
    case PROP_TEST_OBJ_HASH_TABLE_OLD:
      if (self->hash_table != NULL)
        g_hash_table_ref (self->hash_table);
      g_value_set_boxed (value, self->hash_table);
      break;

    case PROP_TEST_OBJ_LIST:
    case PROP_TEST_OBJ_LIST_OLD:
      g_value_set_pointer (value, self->list);
      break;

    case PROP_TEST_OBJ_INT:
      g_value_set_int (value, self->some_int8);
      break;

    case PROP_TEST_OBJ_FLOAT:
      g_value_set_float (value, self->some_float);
      break;

    case PROP_TEST_OBJ_DOUBLE:
      g_value_set_double (value, self->some_double);
      break;

    case PROP_TEST_OBJ_STRING:
      g_value_set_string (value, self->string);
      break;

    case PROP_TEST_OBJ_GTYPE:
      g_value_set_gtype (value, self->gtype);
      break;

    default:
      /* We don't have any other property... */
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
      break;
    }
}

static void
regress_test_obj_dispose (GObject *gobject)
{
  RegressTestObj *self = REGRESS_TEST_OBJECT (gobject);

  if (self->bare)
    {
      g_object_unref (self->bare);

      self->bare = NULL;
    }

  if (self->boxed)
    {
      regress_test_boxed_free (self->boxed);
      self->boxed = NULL;
    }

  /* Chain up to the parent class */
  G_OBJECT_CLASS (regress_test_obj_parent_class)->dispose (gobject);
}

static int
regress_test_obj_default_matrix (RegressTestObj *obj, const char *somestr)
{
  return 42;
}

enum {
  REGRESS_TEST_OBJ_SIGNAL_SIG_NEW_WITH_ARRAY_PROP,
  REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_HASH_PROP,
  REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_STRV,
  REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_OBJ,
  REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_FOREIGN_STRUCT,
  REGRESS_TEST_OBJ_SIGNAL_FIRST,
  REGRESS_TEST_OBJ_SIGNAL_CLEANUP,
  REGRESS_TEST_OBJ_SIGNAL_ALL,
  REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_INT64_PROP,
  REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_UINT64_PROP,
  REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_INTARRAY_RET,
  N_REGRESS_TEST_OBJ_SIGNALS
};

static guint regress_test_obj_signals[N_REGRESS_TEST_OBJ_SIGNALS] = { 0 };

static void
regress_test_obj_class_init (RegressTestObjClass *klass)
{
  GObjectClass *gobject_class = G_OBJECT_CLASS (klass);
  GParamSpec *pspec;
  GType param_types[1];

  klass->test_signal =
    g_signal_newv ("test",
                   G_TYPE_FROM_CLASS (gobject_class),
                   G_SIGNAL_RUN_LAST | G_SIGNAL_NO_RECURSE | G_SIGNAL_NO_HOOKS,
                   NULL /* closure */,
                   NULL /* accumulator */,
                   NULL /* accumulator data */,
                   g_cclosure_marshal_VOID__VOID,
                   G_TYPE_NONE /* return_type */,
                   0     /* n_params */,
                   NULL  /* param_types */);

  param_types[0] = regress_test_simple_boxed_a_get_gtype() | G_SIGNAL_TYPE_STATIC_SCOPE;
  klass->test_signal_with_static_scope_arg =
    g_signal_newv ("test-with-static-scope-arg",
                   G_TYPE_FROM_CLASS (gobject_class),
                   G_SIGNAL_RUN_LAST | G_SIGNAL_NO_RECURSE | G_SIGNAL_NO_HOOKS,
                   NULL /* closure */,
                   NULL /* accumulator */,
                   NULL /* accumulator data */,
                   g_cclosure_marshal_VOID__BOXED,
                   G_TYPE_NONE /* return_type */,
                   1     /* n_params */,
                   param_types);

  /**
   * RegressTestObj::sig-with-array-prop:
   * @self: an object
   * @arr: (type GArray) (element-type uint): numbers
   *
   * This test signal is like TelepathyGlib's
   *  TpChannel:: group-members-changed-detailed:
   */
  regress_test_obj_signals[REGRESS_TEST_OBJ_SIGNAL_SIG_NEW_WITH_ARRAY_PROP] =
    g_signal_new ("sig-with-array-prop",
		  G_TYPE_FROM_CLASS (gobject_class),
		  G_SIGNAL_RUN_LAST,
		  0,
		  NULL,
		  NULL,
		  g_cclosure_marshal_VOID__BOXED,
		  G_TYPE_NONE,
		  1,
		  G_TYPE_ARRAY);

  /**
   * RegressTestObj::sig-with-hash-prop:
   * @self: an object
   * @hash: (element-type utf8 GObject.Value):
   *
   * This test signal is like TelepathyGlib's
   *  TpAccount::status-changed
   */
  regress_test_obj_signals[REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_HASH_PROP] =
    g_signal_new ("sig-with-hash-prop",
		  G_TYPE_FROM_CLASS (gobject_class),
		  G_SIGNAL_RUN_LAST,
		  0,
		  NULL,
		  NULL,
		  g_cclosure_marshal_VOID__BOXED,
		  G_TYPE_NONE,
		  1,
		  G_TYPE_HASH_TABLE);

  /**
   * RegressTestObj::sig-with-strv:
   * @self: an object
   * @strs: strings
   *
   * Test GStrv as a param.
   */
  regress_test_obj_signals[REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_STRV] =
    g_signal_new ("sig-with-strv",
		  G_TYPE_FROM_CLASS (gobject_class),
		  G_SIGNAL_RUN_LAST,
		  0,
		  NULL,
		  NULL,
		  g_cclosure_marshal_VOID__BOXED,
		  G_TYPE_NONE,
		  1,
		  G_TYPE_STRV);

   /**
   * RegressTestObj::sig-with-obj:
   * @self: an object
   * @obj: (transfer none): A newly created RegressTestObj
   *
   * Test transfer none GObject as a param (tests refcounting).
   * Use with regress_test_obj_emit_sig_with_obj
   */
  regress_test_obj_signals[REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_OBJ] =
    g_signal_new ("sig-with-obj",
		  G_TYPE_FROM_CLASS (gobject_class),
		  G_SIGNAL_RUN_LAST,
		  0,
		  NULL,
		  NULL,
		  g_cclosure_marshal_VOID__OBJECT,
		  G_TYPE_NONE,
		  1,
		  G_TYPE_OBJECT);

#ifndef _GI_DISABLE_CAIRO
   /**
   * RegressTestObj::sig-with-foreign-struct:
   * @self: an object
   * @cr: (transfer none): A cairo context.
   */
  regress_test_obj_signals[REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_FOREIGN_STRUCT] =
    g_signal_new ("sig-with-foreign-struct",
		  G_TYPE_FROM_CLASS (gobject_class),
		  G_SIGNAL_RUN_LAST,
		  0,
		  NULL,
		  NULL,
                  NULL,
		  G_TYPE_NONE,
		  1,
		  CAIRO_GOBJECT_TYPE_CONTEXT);
#endif

  regress_test_obj_signals[REGRESS_TEST_OBJ_SIGNAL_FIRST] =
    g_signal_new ("first",
		  G_TYPE_FROM_CLASS (gobject_class),
		  G_SIGNAL_RUN_FIRST,
		  0,
		  NULL,
		  NULL,
		  g_cclosure_marshal_VOID__VOID,
		  G_TYPE_NONE,
                  0);

    regress_test_obj_signals[REGRESS_TEST_OBJ_SIGNAL_CLEANUP] =
    g_signal_new ("cleanup",
		  G_TYPE_FROM_CLASS (gobject_class),
		  G_SIGNAL_RUN_CLEANUP,
		  0,
		  NULL,
		  NULL,
		  g_cclosure_marshal_VOID__VOID,
		  G_TYPE_NONE,
                  0);

    regress_test_obj_signals[REGRESS_TEST_OBJ_SIGNAL_ALL] =
    g_signal_new ("all",
		  G_TYPE_FROM_CLASS (gobject_class),
		  G_SIGNAL_RUN_FIRST | G_SIGNAL_NO_RECURSE | G_SIGNAL_DETAILED | G_SIGNAL_ACTION | G_SIGNAL_NO_HOOKS,
		  0,
		  NULL,
		  NULL,
		  g_cclosure_marshal_VOID__VOID,
		  G_TYPE_NONE,
                  0);

  /**
   * RegressTestObj::sig-with-int64-prop:
   * @self: an object
   * @i: an integer
   *
   * You can use this with regress_test_obj_emit_sig_with_int64, or raise from
   * the introspection client langage.
   */
  regress_test_obj_signals[REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_INT64_PROP] =
    g_signal_new ("sig-with-int64-prop",
		  G_TYPE_FROM_CLASS (gobject_class),
		  G_SIGNAL_RUN_LAST,
		  0,
		  NULL,
		  NULL,
		  g_cclosure_marshal_VOID__BOXED,
		  G_TYPE_INT64,
		  1,
		  G_TYPE_INT64);

  /**
   * RegressTestObj::sig-with-uint64-prop:
   * @self: an object
   * @i: an integer
   *
   * You can use this with regress_test_obj_emit_sig_with_uint64, or raise from
   * the introspection client langage.
   */
  regress_test_obj_signals[REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_UINT64_PROP] =
    g_signal_new ("sig-with-uint64-prop",
		  G_TYPE_FROM_CLASS (gobject_class),
		  G_SIGNAL_RUN_LAST,
		  0,
		  NULL,
		  NULL,
		  g_cclosure_marshal_VOID__BOXED,
		  G_TYPE_UINT64,
		  1,
		  G_TYPE_UINT64);

  /**
   * RegressTestObj::sig-with-intarray-ret:
   * @self: an object
   * @i: an integer
   *
   * Returns: (array zero-terminated=1) (element-type gint) (transfer full):
   */
  regress_test_obj_signals[REGRESS_TEST_OBJ_SIGNAL_SIG_WITH_INTARRAY_RET] =
    g_signal_new ("sig-with-intarray-ret",
		  G_TYPE_FROM_CLASS (gobject_class),
		  G_SIGNAL_RUN_LAST,
		  0,
		  NULL,
		  NULL,
		  g_cclosure_marshal_VOID__BOXED,
		  G_TYPE_ARRAY,
		  1,
		  G_TYPE_INT);

  gobject_class->set_property = regress_test_obj_set_property;
  gobject_class->get_property = regress_test_obj_get_property;
  gobject_class->dispose = regress_test_obj_dispose;

  pspec = g_param_spec_object ("bare",
                               "Bare property",
                               "A contained object",
                               G_TYPE_OBJECT,
                               G_PARAM_READWRITE);
  g_object_class_install_property (gobject_class,
                                   PROP_TEST_OBJ_BARE,
                                   pspec);

  pspec = g_param_spec_boxed ("boxed",
                              "Boxed property",
                              "A contained boxed struct",
                              REGRESS_TEST_TYPE_BOXED,
                              G_PARAM_READWRITE);
  g_object_class_install_property (gobject_class,
                                   PROP_TEST_OBJ_BOXED,
                                   pspec);

  /**
   * RegressTestObj:hash-table:
   *
   * Type: GLib.HashTable(utf8,gint8)
   * Transfer: container
   */
  pspec = g_param_spec_boxed ("hash-table",
                              "GHashTable property",
                              "A contained GHashTable",
                              G_TYPE_HASH_TABLE,
                              G_PARAM_READWRITE);
  g_object_class_install_property (gobject_class,
                                   PROP_TEST_OBJ_HASH_TABLE,
                                   pspec);

  /**
   * RegressTestObj:list:
   *
   * Type: GLib.List(utf8)
   * Transfer: none
   */
  pspec = g_param_spec_pointer ("list",
                                "GList property",
                                "A contained GList",
                                G_PARAM_READWRITE);
  g_object_class_install_property (gobject_class,
                                   PROP_TEST_OBJ_LIST,
                                   pspec);

  /**
   * RegressTestObj:hash-table-old:
   *
   * Type: GLib.HashTable<utf8,gint8>
   * Transfer: container
   */
  pspec = g_param_spec_boxed ("hash-table-old",
                              "GHashTable property with <>",
                              "A contained GHashTable with <>",
                              G_TYPE_HASH_TABLE,
                              G_PARAM_READWRITE);
  g_object_class_install_property (gobject_class,
                                   PROP_TEST_OBJ_HASH_TABLE_OLD,
                                   pspec);

  /**
   * RegressTestObj:list-old:
   *
   * Type: GLib.List<utf8>
   * Transfer: none
   */
  pspec = g_param_spec_pointer ("list-old",
                                "GList property with ()",
                                "A contained GList with <>",
                                G_PARAM_READWRITE);
  g_object_class_install_property (gobject_class,
                                   PROP_TEST_OBJ_LIST_OLD,
                                   pspec);



  /**
   * TestObj:int:
   */
  pspec = g_param_spec_int ("int",
                            "int property",
                            "A contained int",
                            G_MININT,
                            G_MAXINT,
                            0,
                            G_PARAM_READWRITE);
  g_object_class_install_property (gobject_class,
                                   PROP_TEST_OBJ_INT,
                                   pspec);

  /**
   * TestObj:float:
   */
  pspec = g_param_spec_float ("float",
                              "float property",
                              "A contained float",
                              G_MINFLOAT,
                              G_MAXFLOAT,
                              1.0f,
                              G_PARAM_READWRITE);
  g_object_class_install_property (gobject_class,
                                   PROP_TEST_OBJ_FLOAT,
                                   pspec);

  /**
   * TestObj:double:
   */
  pspec = g_param_spec_double ("double",
                               "double property",
                               "A contained double",
                               G_MINDOUBLE,
                               G_MAXDOUBLE,
                               1.0f,
                               G_PARAM_READWRITE);
  g_object_class_install_property (gobject_class,
                                   PROP_TEST_OBJ_DOUBLE,
                                   pspec);

  /**
   * TestObj:string:
   */
  pspec = g_param_spec_string ("string",
                               "string property",
                               "A contained string",
                               NULL,
                               G_PARAM_READWRITE);
  g_object_class_install_property (gobject_class,
                                   PROP_TEST_OBJ_STRING,
                                   pspec);


  /**
   * TestObj:gtype:
   */
  pspec = g_param_spec_gtype ("gtype",
                              "GType property",
                              "A GType property",
                              G_TYPE_NONE,
                              G_PARAM_READWRITE);
  g_object_class_install_property (gobject_class,
                                   PROP_TEST_OBJ_GTYPE,
                                   pspec);

  klass->matrix = regress_test_obj_default_matrix;
}

static void
regress_test_obj_init (RegressTestObj *obj)
{
  obj->bare = NULL;
  obj->boxed = NULL;
  obj->hash_table = NULL;
  obj->gtype = G_TYPE_INVALID;
}

/**
 * regress_test_obj_new: (constructor)
 * @obj: A #RegressTestObj
 */
RegressTestObj *
regress_test_obj_new (RegressTestObj *obj)
{
  return g_object_new (REGRESS_TEST_TYPE_OBJ, NULL);
}

/**
 * regress_constructor: (constructor)
 *
 */
RegressTestObj *
regress_constructor (void)
{
  return g_object_new (REGRESS_TEST_TYPE_OBJ, NULL);
}

/**
 * regress_test_obj_new_from_file:
 */
RegressTestObj *
regress_test_obj_new_from_file (const char *x, GError **error)
{
  return g_object_new (REGRESS_TEST_TYPE_OBJ, NULL);
}

/**
 * regress_test_obj_set_bare:
 * @bare: (allow-none):
 */
void
regress_test_obj_set_bare (RegressTestObj *obj, GObject *bare)
{
  if (obj->bare)
    g_object_unref (obj->bare);
  obj->bare = bare;
  if (obj->bare)
    g_object_ref (obj->bare);
}

void
regress_test_obj_emit_sig_with_obj (RegressTestObj *obj)
{
    RegressTestObj *obj_param = regress_constructor ();
    g_object_set (obj_param, "int", 3, NULL);
    g_signal_emit_by_name (obj, "sig-with-obj", obj_param);
    g_object_unref (obj_param);
}

#ifndef _GI_DISABLE_CAIRO
void
regress_test_obj_emit_sig_with_foreign_struct (RegressTestObj *obj)
{
  cairo_t *cr = regress_test_cairo_context_full_return ();
  g_signal_emit_by_name (obj, "sig-with-foreign-struct", cr);
  cairo_destroy (cr);
}
#endif

void
regress_test_obj_emit_sig_with_int64 (RegressTestObj *obj)
{
  gint64 ret = 0;
  RegressTestObj *obj_param = regress_constructor ();
  g_signal_emit_by_name (obj, "sig-with-int64-prop", G_MAXINT64, &ret);
  g_object_unref (obj_param);
  g_assert (ret == G_MAXINT64);
}

void
regress_test_obj_emit_sig_with_uint64 (RegressTestObj *obj)
{
  guint64 ret = 0;
  RegressTestObj *obj_param = regress_constructor ();
  g_signal_emit_by_name (obj, "sig-with-uint64-prop", G_MAXUINT64, &ret);
  g_object_unref (obj_param);
  g_assert (ret == G_MAXUINT64);
}

int
regress_test_obj_instance_method (RegressTestObj *obj)
{
    return -1;
}

double
regress_test_obj_static_method (int x)
{
  return x;
}

/**
 * regress_forced_method: (method)
 * @obj: A #RegressTestObj
 *
 */
void
regress_forced_method (RegressTestObj *obj)
{
}

/**
 * regress_test_obj_torture_signature_0:
 * @obj: A #RegressTestObj
 * @x:
 * @y: (out):
 * @z: (out):
 * @foo:
 * @q: (out):
 * @m:
 *
 */
void
regress_test_obj_torture_signature_0 (RegressTestObj    *obj,
                              int         x,
                              double     *y,
                              int        *z,
                              const char *foo,
                              int        *q,
                              guint       m)
{
  *y = x;
  *z = x * 2;
  *q = g_utf8_strlen (foo, -1) + m;
}

/**
 * regress_test_obj_torture_signature_1:
 * @obj: A #RegressTestObj
 * @x:
 * @y: (out):
 * @z: (out):
 * @foo:
 * @q: (out):
 * @m:
 * @error: A #GError
 *
 * This function throws an error if m is odd.
 */
gboolean
regress_test_obj_torture_signature_1 (RegressTestObj   *obj,
                              int        x,
                              double     *y,
                              int        *z,
                              const char *foo,
                              int        *q,
                              guint       m,
                              GError    **error)
{
  *y = x;
  *z = x * 2;
  *q = g_utf8_strlen (foo, -1) + m;
  if (m % 2 == 0)
      return TRUE;
  g_set_error (error, G_IO_ERROR, G_IO_ERROR_FAILED, "m is odd");
  return FALSE;
}

/**
 * regress_test_obj_skip_return_val:
 * @obj: a #RegressTestObj
 * @a: Parameter.
 * @out_b: (out): A return value.
 * @c: Other parameter.
 * @inout_d: (inout): Will be incremented.
 * @out_sum: (out): Return value.
 * @num1: Number.
 * @num2: Number.
 * @error: Return location for error.
 *
 * Check that the return value is skipped
 *
 * Returns: (skip): %TRUE if the call succeeds, %FALSE if @error is set.
 */
gboolean
regress_test_obj_skip_return_val (RegressTestObj *obj,
                                  gint            a,
                                  gint           *out_b,
                                  gdouble         c,
                                  gint           *inout_d,
                                  gint           *out_sum,
                                  gint            num1,
                                  gint            num2,
                                  GError        **error)
{
  if (out_b != NULL)
    *out_b = a + 1;
  if (inout_d != NULL)
    *inout_d = *inout_d + 1;
  if (out_sum != NULL)
    *out_sum = num1 + 10*num2;
  return TRUE;
}

/**
 * regress_test_obj_skip_return_val_no_out:
 * @obj: a #RegressTestObj
 * @a: Parameter.
 * @error: Return location for error.
 *
 * Check that the return value is skipped. Succeed if a is nonzero, otherwise
 * raise an error.
 *
 * Returns: (skip): %TRUE if the call succeeds, %FALSE if @error is set.
 */
gboolean
regress_test_obj_skip_return_val_no_out (RegressTestObj *obj,
                                         gint            a,
                                         GError        **error)
{
  if (a == 0) {
    g_set_error (error, G_IO_ERROR, G_IO_ERROR_FAILED, "a is zero");
    return FALSE;
  } else {
    return TRUE;
  }
}

/**
 * regress_test_obj_skip_param:
 * @obj: A #RegressTestObj.
 * @a: Parameter.
 * @out_b: (out): Return value.
 * @c: (skip): Other parameter.
 * @inout_d: (inout): Will be incremented.
 * @out_sum: (out): Return value.
 * @num1: Number.
 * @num2: Number.
 * @error: Return location for error.
 *
 * Check that a parameter is skipped
 *
 * Returns: %TRUE if the call succeeds, %FALSE if @error is set.
 */
gboolean
regress_test_obj_skip_param (RegressTestObj *obj,
                             gint            a,
                             gint           *out_b,
                             gdouble         c,
                             gint           *inout_d,
                             gint           *out_sum,
                             gint            num1,
                             gint            num2,
                             GError        **error)
{
  if (out_b != NULL)
    *out_b = a + 1;
  if (inout_d != NULL)
    *inout_d = *inout_d + 1;
  if (out_sum != NULL)
    *out_sum = num1 + 10*num2;
  return TRUE;
}

/**
 * regress_test_obj_skip_out_param:
 * @obj: A #RegressTestObj.
 * @a: Parameter.
 * @out_b: (out) (skip): Return value.
 * @c: Other parameter.
 * @inout_d: (inout): Will be incremented.
 * @out_sum: (out): Return value.
 * @num1: Number.
 * @num2: Number.
 * @error: Return location for error.
 *
 * Check that the out value is skipped
 *
 * Returns: %TRUE if the call succeeds, %FALSE if @error is set.
 */
gboolean
regress_test_obj_skip_out_param (RegressTestObj *obj,
                                 gint            a,
                                 gint           *out_b,
                                 gdouble         c,
                                 gint           *inout_d,
                                 gint           *out_sum,
                                 gint            num1,
                                 gint            num2,
                                 GError        **error)
{
  if (out_b != NULL)
    *out_b = a + 1;
  if (inout_d != NULL)
    *inout_d = *inout_d + 1;
  if (out_sum != NULL)
    *out_sum = num1 + 10*num2;
  return TRUE;
}

/**
 * regress_test_obj_skip_inout_param:
 * @obj: A #RegressTestObj.
 * @a: Parameter.
 * @out_b: (out): Return value.
 * @c: Other parameter.
 * @inout_d: (inout) (skip): Will be incremented.
 * @out_sum: (out): Return value.
 * @num1: Number.
 * @num2: Number.
 * @error: Return location for error.
 *
 * Check that the out value is skipped
 *
 * Returns: %TRUE if the call succeeds, %FALSE if @error is set.
 */
gboolean
regress_test_obj_skip_inout_param (RegressTestObj *obj,
                                   gint            a,
                                   gint           *out_b,
                                   gdouble         c,
                                   gint           *inout_d,
                                   gint           *out_sum,
                                   gint            num1,
                                   gint            num2,
                                   GError        **error)
{
  if (out_b != NULL)
    *out_b = a + 1;
  if (inout_d != NULL)
    *inout_d = *inout_d + 1;
  if (out_sum != NULL)
    *out_sum = num1 + 10*num2;
  return TRUE;
}

/**
 * regress_test_obj_do_matrix:
 * @obj: A #RegressTestObj
 * @somestr: Meaningless string
 *
 * This method is virtual.  Notably its name differs from the virtual
 * slot name, which makes it useful for testing bindings handle this
 * case.
 *
 * Virtual: matrix
 */
int
regress_test_obj_do_matrix (RegressTestObj *obj, const char *somestr)
{
  return REGRESS_TEST_OBJ_GET_CLASS (obj)->matrix (obj, somestr);
}

/**
 * regress_func_obj_null_in:
 * @obj: (allow-none): A #RegressTestObj
 */
void
regress_func_obj_null_in (RegressTestObj *obj)
{
}

/**
 * regress_test_obj_null_out:
 * @obj: (allow-none) (out): A #RegressTestObj
 */
void
regress_test_obj_null_out (RegressTestObj **obj)
{
  if (obj)
    *obj = NULL;
}

/**
 * regress_test_array_fixed_out_objects:
 * @objs: (out) (array fixed-size=2) (transfer full): An array of #RegressTestObj
 */
void
regress_test_array_fixed_out_objects (RegressTestObj ***objs)
{
    RegressTestObj **values = (RegressTestObj**)g_new(gpointer, 2);

    values[0] = regress_constructor();
    values[1] = regress_constructor();

    *objs = values;
}

typedef struct _CallbackInfo CallbackInfo;

struct _CallbackInfo
{
  RegressTestCallbackUserData callback;
  GDestroyNotify notify;
  gpointer user_data;
};


G_DEFINE_TYPE(RegressTestSubObj, regress_test_sub_obj, REGRESS_TEST_TYPE_OBJ);

static void
regress_test_sub_obj_class_init (RegressTestSubObjClass *klass)
{
}

static void
regress_test_sub_obj_init (RegressTestSubObj *obj)
{
}

RegressTestObj*
regress_test_sub_obj_new ()
{
  return g_object_new (REGRESS_TEST_TYPE_SUB_OBJ, NULL);
}

int
regress_test_sub_obj_instance_method (RegressTestSubObj *obj)
{
    return 0;
}

void
regress_test_sub_obj_unset_bare (RegressTestSubObj *obj)
{
  regress_test_obj_set_bare(REGRESS_TEST_OBJECT(obj), NULL);
}

/* RegressTestFundamental */

/**
 * regress_test_fundamental_object_ref:
 *
 * Returns: (transfer full): A new #RegressTestFundamentalObject
 */
RegressTestFundamentalObject *
regress_test_fundamental_object_ref (RegressTestFundamentalObject * fundamental_object)
{
  g_return_val_if_fail (fundamental_object != NULL, NULL);
  g_atomic_int_inc (&fundamental_object->refcount);

  return fundamental_object;
}

static void
regress_test_fundamental_object_free (RegressTestFundamentalObject * fundamental_object)
{
  RegressTestFundamentalObjectClass *mo_class;
  regress_test_fundamental_object_ref (fundamental_object);

  mo_class = REGRESS_TEST_FUNDAMENTAL_OBJECT_GET_CLASS (fundamental_object);
  mo_class->finalize (fundamental_object);

  if (G_LIKELY (g_atomic_int_dec_and_test (&fundamental_object->refcount))) {
    g_type_free_instance ((GTypeInstance *) fundamental_object);
  }
}

void
regress_test_fundamental_object_unref (RegressTestFundamentalObject * fundamental_object)
{
  g_return_if_fail (fundamental_object != NULL);
  g_return_if_fail (fundamental_object->refcount > 0);

  if (G_UNLIKELY (g_atomic_int_dec_and_test (&fundamental_object->refcount))) {
    regress_test_fundamental_object_free (fundamental_object);
  }
}

static void
regress_test_fundamental_object_replace (RegressTestFundamentalObject ** olddata, RegressTestFundamentalObject * newdata)
{
  RegressTestFundamentalObject *olddata_val;

  g_return_if_fail (olddata != NULL);

  olddata_val = g_atomic_pointer_get ((gpointer *) olddata);

  if (olddata_val == newdata)
    return;

  if (newdata)
    regress_test_fundamental_object_ref (newdata);

  while (!g_atomic_pointer_compare_and_exchange ((gpointer *) olddata,
          olddata_val, newdata)) {
    olddata_val = g_atomic_pointer_get ((gpointer *) olddata);
  }

  if (olddata_val)
    regress_test_fundamental_object_unref (olddata_val);
}

static void
regress_test_value_fundamental_object_init (GValue * value)
{
  value->data[0].v_pointer = NULL;
}

static void
regress_test_value_fundamental_object_free (GValue * value)
{
  if (value->data[0].v_pointer) {
    regress_test_fundamental_object_unref (REGRESS_TEST_FUNDAMENTAL_OBJECT_CAST (value->data[0].v_pointer));
  }
}

static void
regress_test_value_fundamental_object_copy (const GValue * src_value, GValue * dest_value)
{
  if (src_value->data[0].v_pointer) {
    dest_value->data[0].v_pointer =
        regress_test_fundamental_object_ref (REGRESS_TEST_FUNDAMENTAL_OBJECT_CAST (src_value->data[0].
            v_pointer));
  } else {
    dest_value->data[0].v_pointer = NULL;
  }
}

static gpointer
regress_test_value_fundamental_object_peek_pointer (const GValue * value)
{
  return value->data[0].v_pointer;
}

static gchar *
regress_test_value_fundamental_object_collect (GValue * value,
                                       guint n_collect_values,
                                       GTypeCValue * collect_values,
                                       guint collect_flags)
{
  if (collect_values[0].v_pointer) {
    value->data[0].v_pointer =
        regress_test_fundamental_object_ref (collect_values[0].v_pointer);
  } else {
    value->data[0].v_pointer = NULL;
  }

  return NULL;
}

static gchar *
regress_test_value_fundamental_object_lcopy (const GValue * value,
                                     guint n_collect_values,
                                     GTypeCValue * collect_values,
                                     guint collect_flags)
{
  gpointer *fundamental_object_p = collect_values[0].v_pointer;

  if (!fundamental_object_p) {
    return g_strdup_printf ("value location for '%s' passed as NULL",
        G_VALUE_TYPE_NAME (value));
  }

  if (!value->data[0].v_pointer)
    *fundamental_object_p = NULL;
  else if (collect_flags & G_VALUE_NOCOPY_CONTENTS)
    *fundamental_object_p = value->data[0].v_pointer;
  else
    *fundamental_object_p = regress_test_fundamental_object_ref (value->data[0].v_pointer);

  return NULL;
}

static void
regress_test_fundamental_object_finalize (RegressTestFundamentalObject * obj)
{

}

static RegressTestFundamentalObject *
regress_test_fundamental_object_copy_default (const RegressTestFundamentalObject * obj)
{
  g_warning ("RegressTestFundamentalObject classes must implement RegressTestFundamentalObject::copy");
  return NULL;
}

static void
regress_test_fundamental_object_class_init (gpointer g_class, gpointer class_data)
{
  RegressTestFundamentalObjectClass *mo_class = REGRESS_TEST_FUNDAMENTAL_OBJECT_CLASS (g_class);

  mo_class->copy = regress_test_fundamental_object_copy_default;
  mo_class->finalize = regress_test_fundamental_object_finalize;
}

static void
regress_test_fundamental_object_init (GTypeInstance * instance, gpointer klass)
{
  RegressTestFundamentalObject *fundamental_object = REGRESS_TEST_FUNDAMENTAL_OBJECT_CAST (instance);

  fundamental_object->refcount = 1;
}

/**
 * RegressTestFundamentalObject:
 *
 * Ref Func: regress_test_fundamental_object_ref
 * Unref Func: regress_test_fundamental_object_unref
 * Set Value Func: regress_test_value_set_fundamental_object
 * Get Value Func: regress_test_value_get_fundamental_object
 */

GType
regress_test_fundamental_object_get_type (void)
{
  static GType _test_fundamental_object_type = 0;

  if (G_UNLIKELY (_test_fundamental_object_type == 0)) {
    static const GTypeValueTable value_table = {
      regress_test_value_fundamental_object_init,
      regress_test_value_fundamental_object_free,
      regress_test_value_fundamental_object_copy,
      regress_test_value_fundamental_object_peek_pointer,
      (char *) "p",
      regress_test_value_fundamental_object_collect,
      (char *) "p",
      regress_test_value_fundamental_object_lcopy
    };
    static const GTypeInfo fundamental_object_info = {
      sizeof (RegressTestFundamentalObjectClass),
      NULL, NULL,
      regress_test_fundamental_object_class_init,
      NULL,
      NULL,
      sizeof (RegressTestFundamentalObject),
      0,
      (GInstanceInitFunc) regress_test_fundamental_object_init,
      &value_table
    };
    static const GTypeFundamentalInfo fundamental_object_fundamental_info = {
      (G_TYPE_FLAG_CLASSED | G_TYPE_FLAG_INSTANTIATABLE |
          G_TYPE_FLAG_DERIVABLE | G_TYPE_FLAG_DEEP_DERIVABLE)
    };

    _test_fundamental_object_type = g_type_fundamental_next ();
    g_type_register_fundamental (_test_fundamental_object_type, "RegressTestFundamentalObject",
        &fundamental_object_info, &fundamental_object_fundamental_info, G_TYPE_FLAG_ABSTRACT);

  }

  return _test_fundamental_object_type;
}

/**
 * regress_test_value_set_fundamental_object: (skip)
 * @value:
 * @fundamental_object:
 */
void
regress_test_value_set_fundamental_object (GValue * value, RegressTestFundamentalObject * fundamental_object)
{
  gpointer *pointer_p;

  g_return_if_fail (REGRESS_TEST_VALUE_HOLDS_FUNDAMENTAL_OBJECT (value));
  g_return_if_fail (fundamental_object == NULL || REGRESS_TEST_IS_FUNDAMENTAL_OBJECT (fundamental_object));

  pointer_p = &value->data[0].v_pointer;

  regress_test_fundamental_object_replace ((RegressTestFundamentalObject **) pointer_p, fundamental_object);
}

/**
 * regress_test_value_get_fundamental_object: (skip)
 * @value:
 */
RegressTestFundamentalObject *
regress_test_value_get_fundamental_object (const GValue * value)
{
  g_return_val_if_fail (REGRESS_TEST_VALUE_HOLDS_FUNDAMENTAL_OBJECT (value), NULL);

  return value->data[0].v_pointer;
}

static RegressTestFundamentalObjectClass *parent_class = NULL;

G_DEFINE_TYPE (RegressTestFundamentalSubObject, regress_test_fundamental_sub_object, REGRESS_TEST_TYPE_FUNDAMENTAL_OBJECT);

static RegressTestFundamentalSubObject *
_regress_test_fundamental_sub_object_copy (RegressTestFundamentalSubObject * fundamental_sub_object)
{
  RegressTestFundamentalSubObject *copy;

  copy = regress_test_fundamental_sub_object_new(NULL);
  copy->data = g_strdup(fundamental_sub_object->data);
  return copy;
}

static void
regress_test_fundamental_sub_object_finalize (RegressTestFundamentalSubObject * fundamental_sub_object)
{
  g_return_if_fail (fundamental_sub_object != NULL);

  g_free(fundamental_sub_object->data);
  regress_test_fundamental_object_finalize (REGRESS_TEST_FUNDAMENTAL_OBJECT (fundamental_sub_object));
}

static void
regress_test_fundamental_sub_object_class_init (RegressTestFundamentalSubObjectClass * klass)
{
  parent_class = g_type_class_peek_parent (klass);

  klass->fundamental_object_class.copy = (RegressTestFundamentalObjectCopyFunction) _regress_test_fundamental_sub_object_copy;
  klass->fundamental_object_class.finalize =
      (RegressTestFundamentalObjectFinalizeFunction) regress_test_fundamental_sub_object_finalize;
}

static void
regress_test_fundamental_sub_object_init(RegressTestFundamentalSubObject *object)
{

}

/**
 * regress_test_fundamental_sub_object_new:
 */
RegressTestFundamentalSubObject *
regress_test_fundamental_sub_object_new (const char * data)
{
  RegressTestFundamentalSubObject *object;

  object = (RegressTestFundamentalSubObject *) g_type_create_instance (regress_test_fundamental_sub_object_get_type());
  object->data = g_strdup(data);
  return object;
}


/**
 * regress_test_callback:
 * @callback: (scope call) (allow-none):
 *
 **/
int
regress_test_callback (RegressTestCallback callback)
{
    if (callback != NULL)
        return callback();
    return 0;
}

/**
 * regress_test_multi_callback:
 * @callback: (scope call) (allow-none):
 *
 **/
int
regress_test_multi_callback (RegressTestCallback callback)
{
    int sum = 0;
    if (callback != NULL) {
        sum += callback();
        sum += callback();
    }

    return sum;
}

/**
 * regress_test_array_callback:
 * @callback: (scope call):
 *
 **/
int regress_test_array_callback (RegressTestCallbackArray callback)
{
  static const char *strings[] = { "one", "two", "three" };
  static int ints[] = { -1, 0, 1, 2 };
  int sum = 0;

  sum += callback(ints, 4, strings, 3);
  sum += callback(ints, 4, strings, 3);

  return sum;
}

/**
 * regress_test_simple_callback:
 * @callback: (scope call) (allow-none):
 *
 **/
void
regress_test_simple_callback (RegressTestSimpleCallback callback)
{
    if (callback != NULL)
        callback();

    return;
}

/**
 * regress_test_callback_user_data:
 * @callback: (scope call):
 *
 * Call - callback parameter persists for the duration of the method
 * call and can be released on return.
 **/
int
regress_test_callback_user_data (RegressTestCallbackUserData callback,
                         gpointer user_data)
{
  return callback(user_data);
}

static GSList *notified_callbacks = NULL;

/**
 * regress_test_callback_destroy_notify:
 * @callback: (scope notified):
 *
 * Notified - callback persists until a DestroyNotify delegate
 * is invoked.
 **/
int
regress_test_callback_destroy_notify (RegressTestCallbackUserData callback,
                              gpointer user_data,
                              GDestroyNotify notify)
{
  int retval;
  CallbackInfo *info;

  retval = callback(user_data);

  info = g_slice_new(CallbackInfo);
  info->callback = callback;
  info->notify = notify;
  info->user_data = user_data;

  notified_callbacks = g_slist_prepend(notified_callbacks, info);

  return retval;
}

/**
 * regress_test_callback_destroy_notify_no_user_data:
 * @callback: (scope notified):
 *
 * Adds a scope notified callback with no user data. This can invoke an error
 * condition in bindings which needs to be tested.
 **/
int
regress_test_callback_destroy_notify_no_user_data (RegressTestCallbackUserData callback,
                              GDestroyNotify notify)
{
  return regress_test_callback_destroy_notify(callback, NULL, notify);
}

/**
 * regress_test_callback_thaw_notifications:
 *
 * Invokes all callbacks installed by #test_callback_destroy_notify(),
 * adding up their return values, and removes them, invoking the
 * corresponding destroy notfications.
 *
 * Return value: Sum of the return values of the invoked callbacks.
 */
int
regress_test_callback_thaw_notifications (void)
{
  int retval = 0;
  GSList *node;

  for (node = notified_callbacks; node != NULL; node = node->next)
    {
      CallbackInfo *info = node->data;
      retval += info->callback (info->user_data);
      if (info->notify)
        info->notify (info->user_data);
      g_slice_free (CallbackInfo, info);
    }

  g_slist_free (notified_callbacks);
  notified_callbacks = NULL;

  return retval;
}

static GSList *async_callbacks = NULL;

/**
 * regress_test_callback_async:
 * @callback: (scope async):
 *
 **/
void
regress_test_callback_async (RegressTestCallbackUserData callback,
                     gpointer user_data)
{
  CallbackInfo *info;

  info = g_slice_new(CallbackInfo);
  info->callback = callback;
  info->user_data = user_data;

  async_callbacks = g_slist_prepend(async_callbacks, info);
}

/**
 * regress_test_callback_thaw_async:
 */
int
regress_test_callback_thaw_async (void)
{
  int retval = 0;
  GSList *node;

  for (node = async_callbacks; node != NULL; node = node->next)
    {
      CallbackInfo *info = node->data;
      retval = info->callback (info->user_data);
      g_slice_free (CallbackInfo, info);
    }

  g_slist_free (async_callbacks);
  async_callbacks = NULL;
  return retval;
}

void
regress_test_async_ready_callback (GAsyncReadyCallback callback)
{
  GSimpleAsyncResult *result = g_simple_async_result_new (NULL, callback, NULL,
    regress_test_async_ready_callback);
  g_simple_async_result_complete_in_idle (result);
}

/**
 * regress_test_obj_instance_method_callback:
 * @callback: (scope call) (allow-none):
 *
 **/
void
regress_test_obj_instance_method_callback (RegressTestObj *obj, RegressTestCallback callback)
{
    if (callback != NULL)
        callback();
}

/**
 * regress_test_obj_static_method_callback:
 * @callback: (scope call) (allow-none):
 *
 **/
void
regress_test_obj_static_method_callback (RegressTestCallback callback)
{
    if (callback != NULL)
        callback();
}

/**
 * regress_test_obj_new_callback:
 * @callback: (scope notified):
 **/
RegressTestObj *
regress_test_obj_new_callback (RegressTestCallbackUserData callback, gpointer user_data,
                       GDestroyNotify notify)
{
  CallbackInfo *info;

  callback(user_data);

  info = g_slice_new(CallbackInfo);
  info->callback = callback;
  info->notify = notify;
  info->user_data = user_data;

  notified_callbacks = g_slist_prepend(notified_callbacks, info);

  return g_object_new (REGRESS_TEST_TYPE_OBJ, NULL);
}

/**
 * regress_test_hash_table_callback:
 * @data: (element-type utf8 gint): GHashTable that gets passed to callback
 * @callback: (scope call):
 **/
void
regress_test_hash_table_callback (GHashTable *data, RegressTestCallbackHashtable callback)
{
  callback (data);
}

/**
 * regress_test_gerror_callback:
 * @callback: (scope call):
 **/
void
regress_test_gerror_callback (RegressTestCallbackGError callback)
{
  GError *error;

  error = g_error_new_literal (G_IO_ERROR,
                               G_IO_ERROR_NOT_SUPPORTED,
                               "regression test error");
  callback (error);
  g_error_free (error);
}

/**
 * regress_test_null_gerror_callback:
 * @callback: (scope call):
 **/
void
regress_test_null_gerror_callback (RegressTestCallbackGError callback)
{
  callback (NULL);
}

/**
 * regress_test_owned_gerror_callback:
 * @callback: (scope call):
 **/
void
regress_test_owned_gerror_callback (RegressTestCallbackOwnedGError callback)
{
  GError *error;

  error = g_error_new_literal (G_IO_ERROR,
                               G_IO_ERROR_PERMISSION_DENIED,
                               "regression test owned error");
  callback (error);
}

/**
 * regress_test_skip_unannotated_callback: (skip)
 * @callback: No annotation here
 *
 * Should not emit a warning:
 * https://bugzilla.gnome.org/show_bug.cgi?id=685399
 */
void
regress_test_skip_unannotated_callback (RegressTestCallback callback)
{
}

/* interface */

static void
regress_test_interface_default_init(RegressTestInterfaceIface *iface)
{
}

typedef RegressTestInterfaceIface RegressTestInterfaceInterface;
G_DEFINE_INTERFACE (RegressTestInterface, regress_test_interface, G_TYPE_OBJECT)


/* gobject with non-standard prefix */
G_DEFINE_TYPE(RegressTestWi8021x, regress_test_wi_802_1x, G_TYPE_OBJECT);

enum
{
  PROP_TEST_WI_802_1X_TESTBOOL = 1
};

static void
regress_test_wi_802_1x_set_property (GObject      *object,
                             guint         property_id,
                             const GValue *value,
                             GParamSpec   *pspec)
{
  RegressTestWi8021x *self = REGRESS_TEST_WI_802_1X (object);

  switch (property_id)
    {
    case PROP_TEST_WI_802_1X_TESTBOOL:
      regress_test_wi_802_1x_set_testbool (self, g_value_get_boolean (value));
      break;

    default:
      /* We don't have any other property... */
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
      break;
    }
}

static void
regress_test_wi_802_1x_get_property (GObject    *object,
                        guint       property_id,
                        GValue     *value,
                        GParamSpec *pspec)
{
  RegressTestWi8021x *self = REGRESS_TEST_WI_802_1X (object);

  switch (property_id)
    {
    case PROP_TEST_WI_802_1X_TESTBOOL:
      g_value_set_boolean (value, regress_test_wi_802_1x_get_testbool (self));
      break;

    default:
      /* We don't have any other property... */
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
      break;
    }
}

static void
regress_test_wi_802_1x_dispose (GObject *gobject)
{
  /* Chain up to the parent class */
  G_OBJECT_CLASS (regress_test_wi_802_1x_parent_class)->dispose (gobject);
}

static void
regress_test_wi_802_1x_class_init (RegressTestWi8021xClass *klass)
{
  GObjectClass *gobject_class = G_OBJECT_CLASS (klass);
  GParamSpec *pspec;

  gobject_class->set_property = regress_test_wi_802_1x_set_property;
  gobject_class->get_property = regress_test_wi_802_1x_get_property;
  gobject_class->dispose = regress_test_wi_802_1x_dispose;

  pspec = g_param_spec_boolean ("testbool",
                                "Nick for testbool",
                                "Blurb for testbool",
                                TRUE,
                                G_PARAM_READWRITE);
  g_object_class_install_property (gobject_class,
                                   PROP_TEST_WI_802_1X_TESTBOOL,
                                   pspec);
}

static void
regress_test_wi_802_1x_init (RegressTestWi8021x *obj)
{
  obj->testbool = TRUE;
}

RegressTestWi8021x *
regress_test_wi_802_1x_new (void)
{
  return g_object_new (REGRESS_TEST_TYPE_WI_802_1X, NULL);
}

void
regress_test_wi_802_1x_set_testbool (RegressTestWi8021x *obj, gboolean val)
{
  obj->testbool = val;
}

gboolean
regress_test_wi_802_1x_get_testbool (RegressTestWi8021x *obj)
{
  return obj->testbool;
}

int
regress_test_wi_802_1x_static_method (int x)
{
  return 2*x;
}

/* floating gobject */
G_DEFINE_TYPE(RegressTestFloating, regress_test_floating, G_TYPE_INITIALLY_UNOWNED);

static void
regress_test_floating_finalize(GObject *object)
{
  g_assert(!g_object_is_floating (object));

  G_OBJECT_CLASS(regress_test_floating_parent_class)->finalize(object);
}

static void
regress_test_floating_class_init (RegressTestFloatingClass *klass)
{
  GObjectClass *gobject_class = G_OBJECT_CLASS (klass);
  gobject_class->finalize = regress_test_floating_finalize;
}

static void
regress_test_floating_init (RegressTestFloating *obj)
{
}

/**
 * regress_test_floating_new:
 *
 * Returns:: A new floating #RegressTestFloating
 */
RegressTestFloating *
regress_test_floating_new (void)
{
  return g_object_new (REGRESS_TEST_TYPE_FLOATING, NULL);
}


/**
 * regress_test_torture_signature_0:
 * @x:
 * @y: (out):
 * @z: (out):
 * @foo:
 * @q: (out):
 * @m:
 *
 */
void
regress_test_torture_signature_0 (int         x,
                          double     *y,
                          int        *z,
                          const char *foo,
                          int        *q,
                          guint       m)
{
  *y = x;
  *z = x * 2;
  *q = g_utf8_strlen (foo, -1) + m;
}

/**
 * regress_test_torture_signature_1:
 * @x:
 * @y: (out):
 * @z: (out):
 * @foo:
 * @q: (out):
 * @m:
 * @error: A #GError
 *
 * This function throws an error if m is odd.
 */
gboolean
regress_test_torture_signature_1 (int         x,
                          double     *y,
                          int        *z,
                          const char *foo,
                          int        *q,
                          guint       m,
                          GError    **error)
{
  *y = x;
  *z = x * 2;
  *q = g_utf8_strlen (foo, -1) + m;
  if (m % 2 == 0)
      return TRUE;
  g_set_error (error, G_IO_ERROR, G_IO_ERROR_FAILED, "m is odd");
  return FALSE;
}

/**
 * regress_test_torture_signature_2:
 * @x:
 * @callback:
 * @user_data:
 * @notify:
 * @y: (out):
 * @z: (out):
 * @foo:
 * @q: (out):
 * @m:
 *
 */
void
regress_test_torture_signature_2 (int                   x,
                          RegressTestCallbackUserData  callback,
                          gpointer              user_data,
                          GDestroyNotify        notify,
                          double               *y,
                          int                  *z,
                          const char           *foo,
                          int                  *q,
                          guint                 m)
{
  *y = x;
  *z = x * 2;
  *q = g_utf8_strlen (foo, -1) + m;
  notify (user_data);
}

/**
 * regress_test_date_in_gvalue:
 *
 * Returns: (transfer full):
 */
GValue *
regress_test_date_in_gvalue (void)
{
  GValue *value = g_new0 (GValue, 1);
  GDate *date = g_date_new_dmy (5, 12, 1984);

  g_value_init (value, G_TYPE_DATE);
  g_value_take_boxed (value, date);

  return value;
}

/**
 * regress_test_strv_in_gvalue:
 *
 * Returns: (transfer full):
 */
GValue *
regress_test_strv_in_gvalue (void)
{
  GValue *value = g_new0 (GValue, 1);
  const char *strv[] = { "one", "two", "three", NULL };

  g_value_init (value, G_TYPE_STRV);
  g_value_set_boxed (value, strv);

  return value;
}

/**
 * regress_test_multiline_doc_comments:
 *
 * This is a function.
 *
 * It has multiple lines in the documentation.
 *
 * The sky is blue.
 *
 * You will give me your credit card number.
 */
void
regress_test_multiline_doc_comments (void)
{
}

/**
 * regress_test_nested_parameter:
 * @a: An integer
 *
 * <informaltable>
 *   <tgroup cols="3">
 *     <thead>
 *       <row>
 *         <entry>Syntax</entry>
 *         <entry>Explanation</entry>
 *         <entry>Examples</entry>
 *       </row>
 *     </thead>
 *     <tbody>
 *       <row>
 *         <entry>rgb(@r, @g, @b)</entry>
 *         <entry>An opaque color; @r, @g, @b can be either integers between
 *                0 and 255 or percentages</entry>
 *         <entry><literallayout>rgb(128, 10, 54)
 * rgb(20%, 30%, 0%)</literallayout></entry>
 *       </row>
 *       <row>
 *         <entry>rgba(@r, @g, @b, @a)</entry>
 *         <entry>A translucent color; @r, @g, @b are as in the previous row,
 *                @a is a floating point number between 0 and 1</entry>
 *         <entry><literallayout>rgba(255, 255, 0, 0.5)</literallayout></entry>
 *       </row>
 *    </tbody>
 *  </tgroup>
 * </informaltable>
 *
 * What we're testing here is that the scanner ignores the @a nested inside XML.
 */
void
regress_test_nested_parameter (int a)
{
}

/**
 * regress_introspectable_via_alias:
 *
 */
void
regress_introspectable_via_alias (RegressPtrArrayAlias *data)
{
}

/**
 * regress_not_introspectable_via_alias:
 *
 */
void
regress_not_introspectable_via_alias (RegressVaListAlias ok)
{
}

/**
 * regress_aliased_caller_alloc:
 * @boxed: (out):
 */
void regress_aliased_caller_alloc (RegressAliasedTestBoxed *boxed)
{
  boxed->priv = g_slice_new0 (RegressTestBoxedPrivate);
  boxed->priv->magic = 0xdeadbeef;
}

void
regress_test_struct_fixed_array_frob (RegressTestStructFixedArray *str)
{
  guint i;
  str->just_int = 7;

  for (i = 0; i < G_N_ELEMENTS(str->array); i++)
    str->array[i] = 42 + i;
}

/**
 * regress_has_parameter_named_attrs:
 * @foo: some int
 * @attributes: (type guint32) (array fixed-size=32): list of attributes
 *
 * This test case mirrors GnomeKeyringPasswordSchema from
 * libgnome-keyring.
 */
void
regress_has_parameter_named_attrs (int        foo,
                                   gpointer   attributes)
{
}

/**
 * regress_test_versioning:
 *
 * Since: 1.32.1
 * Deprecated: 1.33.3: Use foobar instead
 * Stability: Unstable
 */
void
regress_test_versioning (void)
{
}
