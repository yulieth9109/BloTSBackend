// SPDX-License-Identifier: MIT 

pragma solidity >= 0.8.17 ;

contract BloTS {
   //Emitted when update function is called
   event UpdatedMessages(string oldStr, string newStr);

   string public message;

   constructor(string memory initMessage) {

      message = initMessage;
   }

   // A public function that accepts a string argument and updates the `message` storage variable.
   function update(string memory newMessage) public {
      string memory oldMsg = message;
      message = newMessage;
      emit UpdatedMessages(oldMsg, newMessage);
   }
}