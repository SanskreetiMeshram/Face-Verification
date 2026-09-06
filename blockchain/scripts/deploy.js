const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("------------------------------------------------------------");
  console.log("Deploying ContentFingerprintRegistry smart contract...");
  console.log(`Network: ${hre.network.name} (Chain ID: ${(await hre.ethers.provider.getNetwork()).chainId})`);
  
  const [deployer] = await hre.ethers.getSigners();
  console.log(`Deployer Account: ${deployer.address}`);
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log(`Deployer Balance: ${hre.ethers.formatEther(balance)} ETH`);

  const ContentFingerprintRegistry = await hre.ethers.getContractFactory("ContentFingerprintRegistry");
  const registry = await ContentFingerprintRegistry.deploy();
  await registry.waitForDeployment();

  const contractAddress = await registry.getAddress();
  console.log("------------------------------------------------------------");
  console.log(`✓ ContentFingerprintRegistry deployed at: ${contractAddress}`);
  console.log("------------------------------------------------------------");

  // Export deployment JSON artifact for backend & frontend
  const artifactPath = path.join(__dirname, "../artifacts/contracts/ContentFingerprintRegistry.sol/ContentFingerprintRegistry.json");
  let abi = [];
  if (fs.existsSync(artifactPath)) {
    const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));
    abi = artifact.abi;
  }

  const deployInfo = {
    network: hre.network.name,
    chainId: Number((await hre.ethers.provider.getNetwork()).chainId),
    contractAddress: contractAddress,
    deployer: deployer.address,
    deployedAt: new Date().toISOString(),
    contractName: "ContentFingerprintRegistry",
    abi: abi
  };

  const outputPaths = [
    path.join(__dirname, "../deployment.json"),
    path.join(__dirname, "../../contracts/ContentFingerprintRegistry.json")
  ];

  for (const outPath of outputPaths) {
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, JSON.stringify(deployInfo, null, 2), "utf8");
    console.log(`Saved deployment info to: ${outPath}`);
  }

  console.log("------------------------------------------------------------");
  console.log("Set the following in your backend .env file:");
  console.log(`CONTRACT_ADDRESS=${contractAddress}`);
  console.log("------------------------------------------------------------");
}

main().catch((error) => {
  console.error("Deployment failed:", error);
  process.exitCode = 1;
});
