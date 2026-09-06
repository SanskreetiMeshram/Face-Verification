const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ContentFingerprintRegistry Smart Contract", function () {
  let registry;
  let owner;
  let addr1;
  let addr2;

  const sampleFingerprint1 = ethers.keccak256(ethers.toUtf8Bytes("canonical-metadata-fingerprint-1"));
  const sampleFingerprint2 = ethers.keccak256(ethers.toUtf8Bytes("canonical-metadata-fingerprint-2"));
  const sampleUrl1 = "https://instagram.com/p/sample_post_123";
  const sampleUrl2 = "https://x.com/sample_creator/status/456789";

  beforeEach(async function () {
    [owner, addr1, addr2] = await ethers.getSigners();
    const ContentFingerprintRegistry = await ethers.getContractFactory("ContentFingerprintRegistry");
    registry = await ContentFingerprintRegistry.deploy();
    await registry.waitForDeployment();
  });

  it("Should initialize with zero records", async function () {
    expect(await registry.totalRecords()).to.equal(0);
  });

  it("Should successfully register a new content fingerprint", async function () {
    const tx = await registry.connect(addr1).registerFingerprint(sampleFingerprint1, sampleUrl1);
    await expect(tx)
      .to.emit(registry, "FingerprintRegistered")
      .withArgs(sampleFingerprint1, sampleUrl1, (await ethers.provider.getBlock("latest")).timestamp, addr1.address);

    expect(await registry.totalRecords()).to.equal(1);
  });

  it("Should accurately verify an existing registered fingerprint", async function () {
    await registry.connect(addr1).registerFingerprint(sampleFingerprint1, sampleUrl1);

    const [exists, timestamp, sourceUrl, submitter] = await registry.verifyFingerprint(sampleFingerprint1);
    expect(exists).to.be.true;
    expect(timestamp).to.be.greaterThan(0);
    expect(sourceUrl).to.equal(sampleUrl1);
    expect(submitter).to.equal(addr1.address);
  });

  it("Should return exists=false for an unregistered fingerprint", async function () {
    const unregistered = ethers.keccak256(ethers.toUtf8Bytes("unregistered-content"));
    const [exists, timestamp, sourceUrl, submitter] = await registry.verifyFingerprint(unregistered);
    expect(exists).to.be.false;
    expect(timestamp).to.equal(0);
    expect(sourceUrl).to.equal("");
    expect(submitter).to.equal(ethers.ZeroAddress);
  });

  it("Should retrieve a record using getRecord()", async function () {
    await registry.connect(owner).registerFingerprint(sampleFingerprint2, sampleUrl2);

    const [storedFp, url, ts, submitter] = await registry.getRecord(sampleFingerprint2);
    expect(storedFp).to.equal(sampleFingerprint2);
    expect(url).to.equal(sampleUrl2);
    expect(ts).to.be.greaterThan(0);
    expect(submitter).to.equal(owner.address);
  });

  it("Should retrieve a record by index using getRecordByIndex()", async function () {
    await registry.connect(addr1).registerFingerprint(sampleFingerprint1, sampleUrl1);
    await registry.connect(addr2).registerFingerprint(sampleFingerprint2, sampleUrl2);

    const [fp0, url0] = await registry.getRecordByIndex(0);
    const [fp1, url1] = await registry.getRecordByIndex(1);

    expect(fp0).to.equal(sampleFingerprint1);
    expect(url0).to.equal(sampleUrl1);
    expect(fp1).to.equal(sampleFingerprint2);
    expect(url1).to.equal(sampleUrl2);
  });

  it("Should reject duplicate fingerprint registrations", async function () {
    await registry.connect(addr1).registerFingerprint(sampleFingerprint1, sampleUrl1);

    await expect(
      registry.connect(addr2).registerFingerprint(sampleFingerprint1, "https://different-url.com")
    ).to.be.revertedWith("Fingerprint already registered on-chain");
  });

  it("Should reject zero fingerprint and empty source URL", async function () {
    await expect(
      registry.registerFingerprint(ethers.ZeroHash, sampleUrl1)
    ).to.be.revertedWith("Invalid fingerprint: cannot be zero");

    await expect(
      registry.registerFingerprint(sampleFingerprint1, "")
    ).to.be.revertedWith("Source URL cannot be empty");
  });
});
