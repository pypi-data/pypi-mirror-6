/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include "atomdict.h"
#include "packagenaming.h"

using namespace PythonHelpers;


namespace DictMethods
{

static bool
init_methods()
{
    return true;
}

}  // namespace DictMethods


PyObject*
AtomDict_New( CAtom* atom, Member* key_validator, Member* value_validator )
{
    PyObjectPtr ptr( PyDict_Type.tp_new( &AtomDict_Type, 0, 0 ) );
    if( !ptr )
        return 0;
    Py_XINCREF( pyobject_cast( key_validator ) );
    Py_XINCREF( pyobject_cast( value_validator ) );
    atomdict_cast( ptr.get() )->key_validator = key_validator;
    atomdict_cast( ptr.get() )->value_validator = value_validator;
    atomdict_cast( ptr.get() )->pointer = new CAtomPointer( atom );
    return ptr.release();
}


/*-----------------------------------------------------------------------------
| AtomDict Type
|----------------------------------------------------------------------------*/
class AtomDictHandler
{

public:

    AtomDictHandler( AtomDict* dict )
    {
        m_dict = newref( pyobject_cast( dict ) );
    }

    PyObject* setdefault( PyObject* args )
    {
        PyObject* key;
        PyObject* value = Py_None;
        if( !PyArg_UnpackTuple( args, "setdefault", 1, 2, &key, &value ) )
            return 0;
        PyObjectPtr item( m_dict.get_item( key ) );
        if( item )
            return item.release();
        key = validate_key( key );

        value = validate_value( value )
    }

protected:

    PyDictPtr m_dict;

private:

    AtomDictHandler();
};


static PyObject*
AtomDict_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObjectPtr ptr( PyDict_Type.tp_new( type, args, kwargs ) );
    if( !ptr )
        return 0;
    atomdict_cast( ptr.get() )->pointer = new CAtomPointer();
    return ptr.release();
}


static void
AtomDict_dealloc( AtomDict* self )
{
    delete self->pointer;
    self->pointer = 0;
    Py_CLEAR( self->key_validator );
    Py_CLEAR( self->value_validator );
    PyDict_Type.tp_dealloc( pyobject_cast( self ) );
}


static PyObject*
AtomDict_setdefault( AtomDict* self, PyObject* args )
{
    return AtomDictHandler( self ).setdefault( args );
}


PyDoc_STRVAR( d_setdefault_doc,
"D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D" );


static PyMethodDef
AtomDict_methods[] = {
    { "setdefault", ( PyCFunction )AtomDict_setdefault, METH_VARARGS, d_setdefault_doc },
    //{ "__reduce_ex__", ( PyCFunction )AtomDict_reduce_ex, METH_O, "" },
    { 0 }  /* sentinel */
};


static PySequenceMethods
AtomDict_as_sequence = {
    (lenfunc)0,                                 /* sq_length */
    (binaryfunc)0,                              /* sq_concat */
    (ssizeargfunc)0,                            /* sq_repeat */
    (ssizeargfunc)0,                            /* sq_item */
    (ssizessizeargfunc)0,                       /* sq_slice */
    (ssizeobjargproc)0,         /* sq_ass_item */
    (ssizessizeobjargproc)0,   /* sq_ass_slice */
    (objobjproc)0,                              /* sq_contains */
    (binaryfunc)0,        /* sq_inplace_concat */
    (ssizeargfunc)0                            /* sq_inplace_repeat */
};


static PyMappingMethods
AtomDict_as_mapping = {
    (lenfunc)0,                             /* mp_length */
    (binaryfunc)0,                          /* mp_subscript */
    (objobjargproc)0   /* mp_ass_subscript */
};


PyTypeObject AtomDict_Type = {
    PyObject_HEAD_INIT( &PyType_Type )
    0,                                      /* ob_size */
    PACKAGE_TYPENAME( "atomdict" ),         /* tp_name */
    sizeof( AtomDict ),                     /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)AtomDict_dealloc,           /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
    (cmpfunc)0,                             /* tp_compare */
    (reprfunc)0,                            /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)&AtomDict_as_sequence, /* tp_as_sequence */
    (PyMappingMethods*)&AtomDict_as_mapping,   /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)0,                         /* tp_call */
    (reprfunc)0,                            /* tp_str */
    (getattrofunc)0,                        /* tp_getattro */
    (setattrofunc)0,                        /* tp_setattro */
    (PyBufferProcs*)0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /* tp_flags */
    0,                                      /* Documentation string */
    (traverseproc)0,                        /* tp_traverse */
    (inquiry)0,                             /* tp_clear */
    (richcmpfunc)0,                         /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    (getiterfunc)0,                         /* tp_iter */
    (iternextfunc)0,                        /* tp_iternext */
    (struct PyMethodDef*)AtomDict_methods,  /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    0,                                      /* tp_getset */
    &PyDict_Type,                           /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)0,                        /* tp_descr_get */
    (descrsetfunc)0,                        /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)0,                           /* tp_alloc */
    (newfunc)AtomDict_new,                  /* tp_new */
    (freefunc)0,                            /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


int
import_atomdict()
{
    if( PyType_Ready( &AtomDict_Type ) < 0 )
        return -1;
    // if( PyType_Ready( &AtomCDict_Type ) < 0 )
    //     return -1;
    if( !DictMethods::init_methods() )
        return -1;
    return 0;
}
