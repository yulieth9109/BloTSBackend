async function main() {
    const BloTS = await ethers.getContractFactory("BloTS");
 
    // Start deployment, returning a promise that resolves to a contract object
    const Hi = await BloTS.deploy("Here you go !!!!");   
    console.log("Contract deployed to address:", Hi.address);
 }
 
 main()
   .then(() => process.exit(0))
   .catch(error => {
     console.error(error);
     process.exit(1);
   });