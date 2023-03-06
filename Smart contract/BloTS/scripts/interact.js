// // interact.js

const API_KEY = process.env.API_KEY;
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS;

const contract = require("../artifacts/contracts/BloTS.sol/BloTS.json");

// provider - Alchemy
const alchemyProvider = new ethers.providers.AlchemyProvider(network="goerli", API_KEY);

// signer - me 
const signer = new ethers.Wallet(PRIVATE_KEY, alchemyProvider);

// contract instance
const helloBloTSContract = new ethers.Contract(CONTRACT_ADDRESS, contract.abi, signer);

async function main() {
    const message = await helloBloTSContract.message();
    console.log("The message is: " + message); 

    console.log("Updating the message...");
    const tx = await helloBloTSContract.update("");
    await tx.wait();

    const newMessage = await helloBloTSContract.message();
    console.log("The new message is: " + newMessage); 
}

main();