/**
 * @file    FluxBound.h
 * @brief   Definition of FluxBound, the SBase derived class of the fbc package.
 * @author  Frank T. Bergmann
 *
 *<!---------------------------------------------------------------------------
 * This file is part of libSBML.  Please visit http://sbml.org for more
 * information about SBML, and the latest version of libSBML.
 *
 * Copyright 2009-2013 California Institute of Technology.
 * 
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation.  A copy of the license agreement is provided
 * in the file named "LICENSE.txt" included with this software distribution
 * and also available online as http://sbml.org/software/libsbml/license.html
 *------------------------------------------------------------------------- -->
 *
 * @class FluxBound
 * @sbmlbrief{fbc} Implementation of the 'fbc' package %FluxBound construct.
 *
 * The FluxBound object holds a single (in)equality that provides the maximum
 * or minimum value that a reaction flux can obtain at steady state.
 */ 

#ifndef FluxBound_H__
#define FluxBound_H__


#include <sbml/common/extern.h>
#include <sbml/common/sbmlfwd.h>
#include <sbml/packages/fbc/common/fbcfwd.h>

LIBSBML_CPP_NAMESPACE_BEGIN

  /**
   * The FluxBoundOperation_t enumeration contains the possible values for
   * the FluxBound 'operation' attribute.  The possible legal values are less
   * than or equal to, greater than or equal to, or equal to.  The two
   * options 'less than' and 'greater than' are not legal values for the
   * FluxBound 'operation' attribute, but are provided to allow backwards
   * compatibility with an earlier version of the draft specification.
   */
typedef enum
{
    FLUXBOUND_OPERATION_LESS_EQUAL /** Less than or equal to. */ 
  , FLUXBOUND_OPERATION_GREATER_EQUAL /** Greater than or equal to.*/ 
  , FLUXBOUND_OPERATION_LESS /** Less than. NOTE:  ILLEGAL VALUE */ 
  , FLUXBOUND_OPERATION_GREATER /** Greater than. NOTE:  ILLEGAL VALUE*/ 
  , FLUXBOUND_OPERATION_EQUAL /** Equal to. */ 
  , FLUXBOUND_OPERATION_UNKNOWN  /** Unknown operation. */
} FluxBoundOperation_t;

LIBSBML_CPP_NAMESPACE_END


#ifdef __cplusplus

#include <string>

#include <sbml/SBase.h>
#include <sbml/ListOf.h>
#include <sbml/packages/fbc/extension/FbcExtension.h>

LIBSBML_CPP_NAMESPACE_BEGIN


class LIBSBML_EXTERN FluxBound : public SBase
{
protected:
  /** @cond doxygenLibsbmlInternal */
  std::string   mId;
  std::string   mName;
  std::string   mReaction;
  FluxBoundOperation_t   mOperation;
  std::string   mOperationString;
  double        mValue;
  /** @endcond */

public:

  /**
   * Creates a new FluxBound with the given level, version, and package version.
   */
   FluxBound(unsigned int level      = FbcExtension::getDefaultLevel(),
         unsigned int version    = FbcExtension::getDefaultVersion(),
         unsigned int pkgVersion = FbcExtension::getDefaultPackageVersion());


  /**
   * Creates a new FluxBound with the given FbcPkgNamespaces object.
   */
   FluxBound(FbcPkgNamespaces* fbcns);


  /**
   * Copy constructor.
   */
   FluxBound(const FluxBound& source);

  /**
   * Assignment operator.
   */
   FluxBound& operator=(const FluxBound& source);


  /**
   * Destructor.
   */ 
  virtual ~FluxBound ();


  /**
   * Returns the value of the "id" attribute of this FluxBound.
   *
   * @return the value of the "id" attribute of this FluxBound.
   */
  virtual const std::string& getId () const;


  /**
   * Predicate returning @c true or @c false depending on whether this
   * FluxBound's "id" attribute has been set.
   *
   * @return @c true if this FluxBound's "id" attribute has been set, 
   * otherwise @c false is returned.
   */
  virtual bool isSetId () const;

  
  /**
   * Sets the value of the "id" attribute of this FluxBound.
   *
   * @return integer value indicating success/failure of the
   * operation. The possible return values are:
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_SUCCESS LIBSBML_OPERATION_SUCCESS @endlink
   * @li @link OperationReturnValues_t#LIBSBML_INVALID_ATTRIBUTE_VALUE LIBSBML_INVALID_ATTRIBUTE_VALUE @endlink
   */
  virtual int setId (const std::string& id);


  /**
   * Unsets the value of the "id" attribute of this FluxBound.
   *
   * @return integer value indicating success/failure of the
   * operation. The possible return values are:
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_SUCCESS LIBSBML_OPERATION_SUCCESS @endlink
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_FAILED LIBSBML_OPERATION_FAILED @endlink
   */
  virtual int unsetId ();
  
  
  /**
   * Returns the value of the "name" attribute of this FluxBound.
   *
   * @return the value of the "name" attribute of this FluxBound.
   */
  virtual const std::string& getName () const;
  
  
  /**
   * Predicate returning @c true or @c false depending on whether this
   * FluxBound's "name" attribute has been set.
   *
   * @return @c true if this FluxBound's "id" attribute has been set,
   * otherwise @c false is returned.
   */
  virtual bool isSetName () const;
  
  
  /**
   * Sets the value of the "name" attribute of this FluxBound.
   *
   * @return integer value indicating success/failure of the
   * operation. The possible return values are:
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_SUCCESS LIBSBML_OPERATION_SUCCESS @endlink
   * @li @link OperationReturnValues_t#LIBSBML_INVALID_ATTRIBUTE_VALUE LIBSBML_INVALID_ATTRIBUTE_VALUE @endlink
   */
  virtual int setName (const std::string& name);
  
  
  /**
   * Unsets the value of the "name" attribute of this FluxBound.
   *
   * @return integer value indicating success/failure of the
   * operation. The possible return values are:
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_SUCCESS LIBSBML_OPERATION_SUCCESS @endlink
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_FAILED LIBSBML_OPERATION_FAILED @endlink
   */
  virtual int unsetName ();

  /**
   * Returns the value of the "reaction" attribute of this FluxBound.
   *
   * @return the value of the "reaction" attribute of this FluxBound.
   */
  virtual const std::string& getReaction () const;


  /**
   * Predicate returning @c true or @c false depending on whether this
   * FluxBound's "reaction" attribute has been set.
   *
   * @return @c true if this FluxBound's "reaction" attribute has been set, 
   * otherwise @c false is returned.
   */
  virtual bool isSetReaction () const;

  
  /**
   * Sets the value of the "reaction" attribute of this FluxBound.
   *
   * @return integer value indicating success/failure of the
   * operation. The possible return values are:
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_SUCCESS LIBSBML_OPERATION_SUCCESS @endlink
   * @li @link OperationReturnValues_t#LIBSBML_INVALID_ATTRIBUTE_VALUE LIBSBML_INVALID_ATTRIBUTE_VALUE @endlink
   */
  virtual int setReaction (const std::string& reaction);


  /**
   * Unsets the value of the "reaction" attribute of this FluxBound.
   *
   * @return integer value indicating success/failure of the
   * operation. The possible return values are:
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_SUCCESS LIBSBML_OPERATION_SUCCESS @endlink
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_FAILED LIBSBML_OPERATION_FAILED @endlink
   */
  virtual int unsetReaction ();


  /**
   * Returns the value of the "operation" attribute of this FluxBound.
   *
   * @return the value of the "operation" attribute of this FluxBound.
   */
  const std::string& getOperation ();


  /**
   * Returns the value of the "operation" attribute of this FluxBound.
   *
   * @return the value of the "operation" attribute of this FluxBound.
   */
  FluxBoundOperation_t getFluxBoundOperation () const;


  /**
   * Predicate returning @c true or @c false depending on whether this
   * FluxBound's "operation" attribute has been set.
   *
   * @return @c true if this FluxBound's "operation" attribute has been set, 
   * otherwise @c false is returned.
   */
  virtual bool isSetOperation () const;

  
  /**
   * Sets the value of the "operation" attribute of this FluxBound.
   *
   * @return integer value indicating success/failure of the
   * operation. The possible return values are:
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_SUCCESS LIBSBML_OPERATION_SUCCESS @endlink
   * @li @link OperationReturnValues_t#LIBSBML_INVALID_ATTRIBUTE_VALUE LIBSBML_INVALID_ATTRIBUTE_VALUE @endlink
   */
  virtual int setOperation (const std::string& operation);


  /**
   * Sets the value of the "operation" attribute of this FluxBound.
   *
   * @return integer value indicating success/failure of the
   * operation. The possible return values are:
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_SUCCESS LIBSBML_OPERATION_SUCCESS @endlink
   * @li @link OperationReturnValues_t#LIBSBML_INVALID_ATTRIBUTE_VALUE LIBSBML_INVALID_ATTRIBUTE_VALUE @endlink
   */
  virtual int setOperation (FluxBoundOperation_t operation);


  /**
   * Unsets the value of the "operation" attribute of this FluxBound.
   *
   * @return integer value indicating success/failure of the
   * operation. The possible return values are:
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_SUCCESS LIBSBML_OPERATION_SUCCESS @endlink
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_FAILED LIBSBML_OPERATION_FAILED @endlink
   */
  virtual int unsetOperation ();

  /**
   * Returns the value of the "value" attribute of this FluxBound.
   *
   * @return the value of the "value" attribute of this FluxBound.
   */
  virtual const double getValue () const;


  /**
   * Predicate returning @c true or @c false depending on whether this
   * FluxBound's "value" attribute has been set.
   *
   * @return @c true if this FluxBound's "value" attribute has been set, 
   * otherwise @c false is returned.
   */
  virtual bool isSetValue () const;

  
  /**
   * Sets the value of the "value" attribute of this FluxBound.
   *
   * @return integer value indicating success/failure of the
   * operation. The possible return values are:
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_SUCCESS LIBSBML_OPERATION_SUCCESS @endlink
   * @li @link OperationReturnValues_t#LIBSBML_INVALID_ATTRIBUTE_VALUE LIBSBML_INVALID_ATTRIBUTE_VALUE @endlink
   */
  virtual int setValue (const double value);


  /**
   * Unsets the value of the "value" attribute of this FluxBound.
   *
   * @return integer value indicating success/failure of the
   * operation. The possible return values are:
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_SUCCESS LIBSBML_OPERATION_SUCCESS @endlink
   * @li @link OperationReturnValues_t#LIBSBML_OPERATION_FAILED LIBSBML_OPERATION_FAILED @endlink
   */
  virtual int unsetValue ();


  /**
   * Renames all the @c SIdRef attributes on this element, including any
   * found in MathML content (if such exists).
   *
   * This method works by looking at all attributes and (if appropriate)
   * mathematical formulas, comparing the identifiers to the value of @p
   * oldid.  If any matches are found, the matching identifiers are replaced
   * with @p newid.  The method does @em not descend into child elements.
   *
   * @param oldid the old identifier
   * @param newid the new identifier
   */
   virtual void renameSIdRefs(const std::string& oldid, const std::string& newid);


  /**
   * Returns the XML element name of
   * this SBML object.
   *
   * @return the string of the name of this element.
   */
  virtual const std::string& getElementName () const ;


  /**
   * Creates and returns a deep copy of this FluxBound.
   * 
   * @return a (deep) copy of this FluxBound.
   */
  virtual FluxBound* clone () const;


  /**
   * Returns the libSBML type code of this object instance.
   *
   * @copydetails doc_what_are_typecodes
   *
   * @return the SBML type code for this object:
   * @link SBMLFbcTypeCode_t#SBML_FBC_FLUXBOUND SBML_FBC_FLUXBOUND@endlink
   *
   * @copydetails doc_warning_typecodes_not_unique
   *
   * @see getElementName()
   * @see getPackageName()
   */
  virtual int getTypeCode () const;


  /** @cond doxygenLibsbmlInternal */
  /**
   * Subclasses should override this method to write out their contained
   * SBML objects as XML elements.  Be sure to call your parents
   * implementation of this method as well.  For example:
   *
   *   SBase::writeElements(stream);
   *   mReactants.write(stream);
   *   mProducts.write(stream);
   *   ...
   */
  virtual void writeElements (XMLOutputStream& stream) const;
  /** @endcond */


  /**
   * Accepts the given SBMLVisitor.
   *
   * @return the result of calling <code>v.visit()</code>, which indicates
   * whether or not the Visitor would like to visit the SBML object's next
   * sibling object (if available).
   */
  virtual bool accept (SBMLVisitor& v) const;


  /** @cond doxygenLibsbmlInternal */
  /**
   * Sets the parent SBMLDocument of this SBML object.
   *
   * @param d the SBMLDocument object to use
   */
  virtual void setSBMLDocument (SBMLDocument* d);
  /** @endcond */


  /** @cond doxygenLibsbmlInternal */
  /**
   * Enables/Disables the given package with this element and child
   * elements (if any).
   * (This is an internal implementation for enablePakcage function)
   *
   * @note Subclasses in which one or more child elements are defined
   * must override this function.
   */
  virtual void enablePackageInternal(const std::string& pkgURI,
                                     const std::string& pkgPrefix, bool flag);
  /** @endcond */


  /** @cond doxygenLibsbmlInternal */
  /* function returns true if component has all the required
   * elements
   * needs to be overloaded for each component
   */
  virtual bool hasRequiredElements() const ;
  /** @endcond */

    
protected:
  /** @cond doxygenLibsbmlInternal */
  /**
   * Create and return an SBML object of this class, if present.
   *
   * @return the SBML object corresponding to next XMLToken in the
   * XMLInputStream or NULL if the token was not recognized.
   */
  virtual SBase*
  createObject (XMLInputStream& stream);
  /** @endcond */


  /** @cond doxygenLibsbmlInternal */
  /**
   * Subclasses should override this method to get the list of
   * expected attributes.
   * This function is invoked from corresponding readAttributes()
   * function.
   */
  virtual void addExpectedAttributes(ExpectedAttributes& attributes);
  /** @endcond */


  /** @cond doxygenLibsbmlInternal */
  /**
   * Subclasses should override this method to read values from the given
   * XMLAttributes set into their specific fields.  Be sure to call your
   * parents implementation of this method as well.
   */
  virtual void readAttributes (const XMLAttributes& attributes, 
                               const ExpectedAttributes& expectedAttributes);
  /** @endcond */


  /** @cond doxygenLibsbmlInternal */
  /**
   * Subclasses should override this method to write their XML attributes
   * to the XMLOutputStream.  Be sure to call your parents implementation
   * of this method as well.  For example:
   *
   *   SBase::writeAttributes(stream);
   *   stream.writeAttribute( "id"  , mId   );
   *   stream.writeAttribute( "name", mName );
   *   ...
   */
  virtual void writeAttributes (XMLOutputStream& stream) const;
  /** @endcond */
};


/**
 * @class ListOfFluxBounds
 * @sbmlbrief{fbc} Implementation of the %ListOfFluxBounds construct from the
 * 'fbc' package.
 * 
 * The ListOfFluxBounds is a container for the FluxBound elements of a Model.
 * 
 * @copydetails doc_what_is_listof
 */
class LIBSBML_EXTERN ListOfFluxBounds : public ListOf
{
public:

  /**
   * Creates and returns a deep copy of this ListOfFluxBounds.
   * 
   * @return a (deep) copy of this ListOfFluxBounds.
   */
  virtual ListOfFluxBounds* clone () const;


  /**
   * Creates a new ListOfFluxBounds with the given level, version, and package version.
   */
   ListOfFluxBounds(unsigned int level      = FbcExtension::getDefaultLevel(), 
                unsigned int version    = FbcExtension::getDefaultVersion(), 
                unsigned int pkgVersion = FbcExtension::getDefaultPackageVersion());


  /**
   * Creates a new ListOfFluxBounds with the given FbcPkgNamespaces object.
   */
   ListOfFluxBounds(FbcPkgNamespaces* fbcns);


  /**
   * Get a FluxBound from the ListOfFluxBounds.
   *
   * @param n the index number of the FluxBound to get.
   * 
   * @return the nth FluxBound in this ListOfFluxBounds.
   *
   * @see size()
   */
  virtual FluxBound* get(unsigned int n); 


  /**
   * Get a FluxBound from the ListOfFluxBounds.
   *
   * @param n the index number of the FluxBound to get.
   * 
   * @return the nth FluxBound in this ListOfFluxBounds.
   *
   * @see size()
   */
  virtual const FluxBound * get(unsigned int n) const; 


  /**
   * Get a FluxBound from the ListOfFluxBounds
   * based on its identifier.
   *
   * @param sid a string representing the identifier 
   * of the FluxBound to get.
   * 
   * @return FluxBound in this ListOfFluxBounds
   * with the given @p sid or @c NULL if no such
   * FluxBound exists.
   *
   * @see get(unsigned int n)
   * @see size()
   */
  virtual FluxBound* get (const std::string& sid);


  /**
   * Get a FluxBound from the ListOfFluxBounds
   * based on its identifier.
   *
   * @param sid a string representing the identifier 
   * of the FluxBound to get.
   * 
   * @return FluxBound in this ListOfFluxBounds
   * with the given @p sid or @c NULL if no such
   * FluxBound exists.
   *
   * @see get(unsigned int n)
   * @see size()
   */
  virtual const FluxBound* get (const std::string& sid) const;


  /**
   * Removes the nth item from this ListOfFluxBounds items and returns a pointer to
   * it.
   *
   * The caller owns the returned item and is responsible for deleting it.
   *
   * @param n the index of the item to remove
   *
   * @see size()
   */
  virtual FluxBound* remove (unsigned int n);


  /**
   * Removes item in this ListOfFluxBounds items with the given identifier.
   *
   * The caller owns the returned item and is responsible for deleting it.
   * If none of the items in this list have the identifier @p sid, then @c
   * NULL is returned.
   *
   * @param sid the identifier of the item to remove
   *
   * @return the item removed.  As mentioned above, the caller owns the
   * returned item.
   */
  virtual FluxBound* remove (const std::string& sid);


  /**
   * Returns the libSBML type code for the SBML objects
   * contained in this ListOf object.
   * 
   * @copydetails doc_what_are_typecodes
   *
   * @return the SBML type code for objects contained in this list:
   * @link SBMLTypeCode_t#SBML_FBC_FLUXBOUND SBML_FBC_FLUXBOUND@endlink (default).
   *
   * @see getElementName()
   * @see getPackageName()
   */
  virtual int getItemTypeCode () const;

  /**
   * Returns the XML element name of
   * this SBML object.
   *
   * @return the string of the name of this element.
   */
  virtual const std::string& getElementName () const;


protected:

  /** @cond doxygenLibsbmlInternal */
  /**
   * Create and return an SBML object of this class, if present.
   *
   * @return the SBML object corresponding to next XMLToken in the
   * XMLInputStream or NULL if the token was not recognized.
   */
  virtual SBase* createObject (XMLInputStream& stream);

  virtual void writeXMLNS (XMLOutputStream& stream) const;
  /** @endcond */
};


LIBSBML_CPP_NAMESPACE_END

#endif /* __cplusplus */


#ifndef SWIG

LIBSBML_CPP_NAMESPACE_BEGIN
BEGIN_C_DECLS

/*
 * C API will be added here.
 */

LIBSBML_EXTERN
FluxBound_t *
FluxBound_create(unsigned int level, unsigned int version, unsigned int pkgversion);


LIBSBML_EXTERN
const char *
FluxBound_getId(FluxBound_t * fb);


LIBSBML_EXTERN
int
FluxBound_isSetId(FluxBound_t * fb);


LIBSBML_EXTERN
int
FluxBound_setId(FluxBound_t * fb, const char * id);


LIBSBML_EXTERN
int
FluxBound_unsetId(FluxBound_t * fb);

LIBSBML_EXTERN
const char *
FluxBound_getName(FluxBound_t * fb);


LIBSBML_EXTERN
int
FluxBound_isSetName(FluxBound_t * fb);


LIBSBML_EXTERN
int
FluxBound_setName(FluxBound_t * fb, const char * name);


LIBSBML_EXTERN
int
FluxBound_unsetName(FluxBound_t * fb);


LIBSBML_EXTERN
const char *
FluxBound_getReaction(FluxBound_t * fb);


LIBSBML_EXTERN
int
FluxBound_isSetReaction(FluxBound_t * fb);


LIBSBML_EXTERN
int
FluxBound_setReaction(FluxBound_t * fb, const char * reaction);


LIBSBML_EXTERN
int
FluxBound_unsetReaction(FluxBound_t * fb);


LIBSBML_EXTERN
const char *
FluxBound_getOperation(FluxBound_t * fb);


LIBSBML_EXTERN
int
FluxBound_isSetOperation(FluxBound_t * fb);


LIBSBML_EXTERN
int
FluxBound_setOperation(FluxBound_t * fb, const char * operation);


LIBSBML_EXTERN
int
FluxBound_unsetOperation(FluxBound_t * fb);


LIBSBML_EXTERN
double
FluxBound_getValue(FluxBound_t * fb);


LIBSBML_EXTERN
int
FluxBound_isSetValue(FluxBound_t * fb);


LIBSBML_EXTERN
int
FluxBound_setValue(FluxBound_t * fb, double value);


LIBSBML_EXTERN
int
FluxBound_unsetValue(FluxBound_t * fb);



LIBSBML_EXTERN
const char* 
FluxBoundOperation_toString(FluxBoundOperation_t type);


LIBSBML_EXTERN
FluxBoundOperation_t 
FluxBoundOperation_fromString(const char* s);


LIBSBML_EXTERN
int 
FluxBoundOperation_isValidFluxBoundOperation(FluxBoundOperation_t type);


LIBSBML_EXTERN
int 
FluxBoundOperation_isValidFluxBoundOperationString(const char* s);


END_C_DECLS
LIBSBML_CPP_NAMESPACE_END


#endif  /* !SWIG */
#endif  /* FluxBound_H__ */
