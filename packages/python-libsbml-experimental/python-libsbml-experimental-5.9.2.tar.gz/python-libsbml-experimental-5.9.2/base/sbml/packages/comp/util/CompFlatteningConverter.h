/**
 * @file    CompFlatteningConverter.h
 * @brief   Definition of a first flattening converter.
 * @author  Frank T. Bergmann
 * 
 * <!--------------------------------------------------------------------------
 * This file is part of libSBML.  Please visit http://sbml.org for more
 * information about SBML, and the latest version of libSBML.
 *
 * Copyright (C) 2009-2011 jointly by the following organizations: 
 *     1. California Institute of Technology, Pasadena, CA, USA
 *     2. EMBL European Bioinformatics Institute (EBML-EBI), Hinxton, UK
 *  
 * Copyright (C) 2006-2008 by the California Institute of Technology,
 *     Pasadena, CA, USA 
 *  
 * Copyright (C) 2002-2005 jointly by the following organizations: 
 *     1. California Institute of Technology, Pasadena, CA, USA
 *     2. Japan Science and Technology Agency, Japan
 * 
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation.  A copy of the license agreement is provided
 * in the file named "LICENSE.txt" included with this software distribution
 * and also available online as http://sbml.org/software/libsbml/license.html
 * ---------------------------------------------------------------------- -->
 *
 * @class CompFlatteningConverter
 * @sbmlbrief{comp} Flattening converter for the &ldquo;comp&rdquo; package.
 */

#ifndef CompFlatteningConverter_h
#define CompFlatteningConverter_h

#include <sbml/SBMLNamespaces.h>
#include <sbml/packages/comp/extension/CompModelPlugin.h>
#include <sbml/conversion/SBMLConverter.h>
#include <sbml/conversion/SBMLConverterRegister.h>


#ifdef __cplusplus


LIBSBML_CPP_NAMESPACE_BEGIN


class CompFlatteningConverter : public SBMLConverter
{
public:

  /** @cond doxygenLibsbmlInternal */
  
  /* register with the ConversionRegistry */
  static void init();  

  /** @endcond */


  /**
   * Constructor.
   */
  CompFlatteningConverter();


  /**
   * Copy constructor.
   */
  CompFlatteningConverter(const CompFlatteningConverter&);


  /**
   * Creates and returns a deep copy of this CompFlatteningConverter.
   * 
   * @return a (deep) copy of this CompFlatteningConverter.
   */
  virtual SBMLConverter* clone() const;


  /**
   * This function determines whether a given converter matches the 
   * configuration properties given. 
   * 
   * @param props the properties to match
   * 
   * @return @c true if this converter is a match, @c false otherwise.
   */
  virtual bool matchesProperties(const ConversionProperties &props) const;


  /**
   * Performs the actual conversion.
   * 
   * @return status code represeting success/failure/conversion impossible
   */
  virtual int convert();


  /**
   * Returns the default properties of this converter.
   * 
   * A given converter exposes one or more properties that can be adjusted
   * in order to influence the behavior of the converter.  This method
   * returns the @em default property settings for this converter.  It is
   * meant to be called in order to discover all the settings for the
   * converter object.
   *
   * The properties for the CompFlatteningConverter are:
   * @li "flatten comp": the name of this converter
   * @li "basePath": the base directory to find external references in
   * @li "leavePorts": boolean indicating whether unused ports 
   *   should be listed in the flattened model; default = false
   * @li "listModelDefinitions": boolean indicating whether the model 
   *   definitions should be listed in the flattened model; default = false
   * @li "stripUnflattenablePackages": boolean indicating whether packages 
   *   that cannot be flattened should be removed; default = true
   * @li "performValidation": boolean indicating whether validation should be 
   *   performed. When @c true either an invalid source document or 
   *   an invalid flattened document will cause flattening to fail; default = true
   * @li "abortIfUnflattenable": string indicating the required status of
   *   any unflattenable packages that should cause flattening to fail.
   *   Possible values are "none", "requiredOnly" and "all"; default = requiredOnly
   *
   * @note previously there was an "ignorePackages" option; whose name
   * proved to be very misleading. This option has been deprecated and 
   * replaced by the "stripUnflattenablePackages" but will still work.
   *
   * @return the ConversionProperties object describing the default properties
   * for this converter.
   */
  virtual ConversionProperties getDefaultProperties() const;

private:

  int reconstructDocument(Model* flatmodel); 

  int reconstructDocument(Model* flatmodel, 
                          SBMLDocument &dummyDoc,  bool dummyRecon = false);

  void stripUnflattenablePackages();

  bool getLeavePorts() const;

  bool getLeaveDefinitions() const;

  bool getIgnorePackages() const;

  bool getStripUnflattenablePackages() const;

  bool getPerformValidation() const;

  bool getAbortForAll() const;

  bool getAbortForRequired() const;

  bool getAbortForNone() const;

  bool canBeFlattened();

  void restoreNamespaces();

  std::set<std::pair<std::string, std::string> > mDisabledPackages;


#ifndef SWIG
  typedef std::vector<bool>                     ValueSet;
  typedef std::map<const std::string, ValueSet> PackageValueMap;
  typedef PackageValueMap::iterator             PackageValueIter;
#endif

  PackageValueMap mPackageValues;

  void analyseDocument();

  bool getRequiredStatus(const std::string & package);

  bool getKnownStatus(const std::string& package);

  bool getFlattenableStatus(const std::string& package);

  bool haveUnknownRequiredPackages();

  bool haveUnknownUnrequiredPackages();

  bool haveUnflattenableRequiredPackages();

  bool haveUnflattenableUnrequiredPackages();

};

LIBSBML_CPP_NAMESPACE_END

#endif  /* __cplusplus */

  
#ifndef SWIG

LIBSBML_CPP_NAMESPACE_BEGIN
BEGIN_C_DECLS


END_C_DECLS
LIBSBML_CPP_NAMESPACE_END

#endif  /* !SWIG */
#endif  /* CompFlatteningConverter_h*/

