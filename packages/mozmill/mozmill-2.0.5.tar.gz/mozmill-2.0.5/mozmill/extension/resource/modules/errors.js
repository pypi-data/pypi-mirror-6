/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, you can obtain one at http://mozilla.org/MPL/2.0/. */

var EXPORTED_SYMBOLS = ['ApplicationQuitError',
                        'AssertionError',
                        'BaseError',
                        'TimeoutError'];


/**
 * Creates a new instance of a base error
 *
 * @class Represents the base for custom errors
 * @param {string} [aMessage=Error().message]
 *        The error message to show
 * @param {string} [aFileName=Error().fileName]
 *        The file name where the error has been raised
 * @param {string} [aLineNumber=Error().lineNumber]
 *        The line number of the file where the error has been raised
 * @param {string} [aFunctionName=undefined]
 *        The function name in which the error has been raised
 */
function BaseError(aMessage, aFileName, aLineNumber, aFunctionName) {
  this.name = this.constructor.name;

  var err = new Error();
  if (err.stack) {
    this.stack = err.stack;
  }

  this.message = aMessage || err.message;
  this.fileName = aFileName || err.fileName;
  this.lineNumber = aLineNumber || err.lineNumber;
  this.functionName = aFunctionName;
}


/**
 * Creates a new instance of an application quit error used by Mozmill to
 * indicate that the application is going to shutdown
 *
 * @class Represents an error object thrown when the application is going to shutdown
 * @param {string} [aMessage=Error().message]
 *        The error message to show
 * @param {string} [aFileName=Error().fileName]
 *        The file name where the error has been raised
 * @param {string} [aLineNumber=Error().lineNumber]
 *        The line number of the file where the error has been raised
 * @param {string} [aFunctionName=undefined]
 *        The function name in which the error has been raised
 */
function ApplicationQuitError(aMessage, aFileName, aLineNumber, aFunctionName) {
  BaseError.apply(this, arguments);
}

ApplicationQuitError.prototype = Object.create(BaseError.prototype, {
  constructor : { value : ApplicationQuitError }
});


/**
 * Creates a new instance of an assertion error
 *
 * @class Represents an error object thrown by failing assertions
 * @param {string} [aMessage=Error().message]
 *        The error message to show
 * @param {string} [aFileName=Error().fileName]
 *        The file name where the error has been raised
 * @param {string} [aLineNumber=Error().lineNumber]
 *        The line number of the file where the error has been raised
 * @param {string} [aFunctionName=undefined]
 *        The function name in which the error has been raised
 */
function AssertionError(aMessage, aFileName, aLineNumber, aFunctionName) {
  BaseError.apply(this, arguments);
}

AssertionError.prototype = Object.create(BaseError.prototype, {
  constructor : { value : AssertionError }
});
